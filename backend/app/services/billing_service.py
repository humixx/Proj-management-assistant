"""Billing service — provider-agnostic interface to Stripe and Paddle.

This module centralises all payment-gateway interactions behind a single
``BillingService`` class, keeping route handlers thin and making it
straightforward to swap or add providers in the future.

Design principles
-----------------
* **Provider-agnostic public API** — callers never import ``stripe`` or
  ``paddle_billing`` directly; they call ``BillingService`` methods with a
  ``PaymentProvider`` enum value.
* **Fail-fast configuration** — if a provider's API keys are not
  configured in ``.env``, attempting to use that provider raises a clear
  ``HTTPException`` rather than a cryptic SDK error.
* **Repository pattern** — all DB persistence is delegated to
  ``SubscriptionRepository``; the service never executes raw SQL.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models.subscription import (
    PaymentProvider,
    PlanType,
    Subscription,
    SubscriptionStatus,
)
from app.db.repositories.subscription_repo import SubscriptionRepository

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Provider availability helpers
# ---------------------------------------------------------------------------

def _stripe_configured() -> bool:
    """Return True when Stripe keys are present in environment."""
    return bool(settings.STRIPE_SECRET_KEY)


def _paddle_configured() -> bool:
    """Return True when a Paddle API key is present in environment."""
    return bool(settings.PADDLE_API_KEY)


def _require_provider(provider: PaymentProvider) -> None:
    """Raise 503 if the requested provider is not configured."""
    if provider == PaymentProvider.STRIPE and not _stripe_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured. Set STRIPE_SECRET_KEY in .env.",
        )
    if provider == PaymentProvider.PADDLE and not _paddle_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Paddle is not configured. Set PADDLE_API_KEY in .env.",
        )


# ---------------------------------------------------------------------------
# Stripe helpers (lazy import to avoid startup crash when keys are absent)
# ---------------------------------------------------------------------------

def _get_stripe():
    """Return a configured ``stripe`` module, imported lazily."""
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


async def _stripe_create_checkout(
    customer_email: str,
    success_url: str,
    cancel_url: str,
) -> dict:
    """Create a Stripe Checkout Session and return its URL + session ID.

    We use ``mode="subscription"`` so that Stripe manages the recurring
    billing lifecycle for us.  The 7-day trial is configured via
    ``subscription_data.trial_period_days``.
    """
    stripe = _get_stripe()

    if not settings.STRIPE_PRICE_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="STRIPE_PRICE_ID is not configured. Set it in .env.",
        )

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer_email=customer_email,
        line_items=[{"price": settings.STRIPE_PRICE_ID, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        subscription_data={"trial_period_days": 7},
    )

    return {
        "checkout_url": session.url,
        "session_id": session.id,
        "provider": PaymentProvider.STRIPE.value,
    }


async def _stripe_create_portal(customer_id: str, return_url: str) -> str:
    """Create a Stripe Billing Portal session and return its URL."""
    stripe = _get_stripe()
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session.url


# ---------------------------------------------------------------------------
# Paddle helpers
# ---------------------------------------------------------------------------

async def _paddle_create_checkout(
    customer_email: str,
    success_url: str,
) -> dict:
    """Build a Paddle Checkout link using the Paddle Billing API.

    For Paddle, the checkout is typically opened client-side via
    ``Paddle.js``. Here we return the transaction preview URL that
    Paddle.js can consume, or a direct hosted checkout link.
    """
    import httpx

    base_url = (
        "https://sandbox-api.paddle.com"
        if settings.PADDLE_ENVIRONMENT == "sandbox"
        else "https://api.paddle.com"
    )

    if not settings.PADDLE_PRICE_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PADDLE_PRICE_ID is not configured. Set it in .env.",
        )

    headers = {
        "Authorization": f"Bearer {settings.PADDLE_API_KEY}",
        "Content-Type": "application/json",
    }

    payload: dict = {
        "items": [{"price_id": settings.PADDLE_PRICE_ID, "quantity": 1}],
        "checkout": {"url": success_url},
        "customer": {"email": customer_email},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/transactions",
            json=payload,
            headers=headers,
            timeout=15.0,
        )
        if not response.is_success:
            logger.error(
                "Paddle API error %s: %s", response.status_code, response.text
            )
            response.raise_for_status()
        data = response.json()

    transaction = data.get("data", {})
    txn_id = transaction.get("id", "")

    # Build the Paddle-hosted checkout URL from the transaction ID
    checkout_base = (
        "https://sandbox-checkout.paddle.com"
        if settings.PADDLE_ENVIRONMENT == "sandbox"
        else "https://checkout.paddle.com"
    )
    checkout_url = f"{checkout_base}/transactions/{txn_id}" if txn_id else ""

    return {
        "checkout_url": checkout_url,
        "session_id": txn_id,
        "provider": PaymentProvider.PADDLE.value,
    }


async def _paddle_get_portal_url(customer_id: str) -> str:
    """Retrieve the Paddle customer portal URL.

    Paddle's customer portal is auto-generated for each customer;
    we simply look it up via the API.
    """
    import httpx

    base_url = (
        "https://sandbox-api.paddle.com"
        if settings.PADDLE_ENVIRONMENT == "sandbox"
        else "https://api.paddle.com"
    )

    headers = {"Authorization": f"Bearer {settings.PADDLE_API_KEY}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/customers/{customer_id}",
            headers=headers,
            timeout=15.0,
        )
        response.raise_for_status()
        data = response.json()

    # Paddle returns a portal URL in the customer object
    customer = data.get("data", {})
    return customer.get("portal_sessions_url", "")


# ---------------------------------------------------------------------------
# Public service class
# ---------------------------------------------------------------------------

class BillingService:
    """High-level billing operations consumed by API route handlers.

    Each method accepts a ``db`` session so that the service remains
    stateless and compatible with FastAPI's request-scoped dependency
    injection.
    """

    # -- Subscription lifecycle --------------------------------------------

    @staticmethod
    async def get_or_create_subscription(
        db: AsyncSession,
        user_id: UUID,
    ) -> Subscription:
        """Return the user's subscription, creating a trial if none exists.

        This is the single source of truth for "does this user have a
        subscription row?"  Call it freely — it is idempotent.
        """
        repo = SubscriptionRepository(db)
        subscription = await repo.get_by_user_id(user_id)
        if subscription is None:
            subscription = await repo.create_trial(user_id)
            logger.info("Created trial subscription for user %s", user_id)
        return subscription

    # -- Checkout ----------------------------------------------------------

    @staticmethod
    async def create_checkout_session(
        db: AsyncSession,
        user_id: UUID,
        user_email: str,
        provider: PaymentProvider,
        success_url: str = "",
        cancel_url: str = "",
    ) -> dict:
        """Create a checkout session with the given provider.

        Args:
            db: Async database session.
            user_id: Authenticated user's UUID.
            user_email: User's email for pre-filling the checkout form.
            provider: ``stripe`` or ``paddle``.
            success_url: URL to redirect to on successful payment.
            cancel_url: URL to redirect to if the user cancels.

        Returns:
            A dict with ``checkout_url``, ``session_id``, and ``provider``.

        Raises:
            HTTPException: If the provider is not configured (503) or if the
                provider's API returns an error (502).
        """
        _require_provider(provider)

        # Ensure a subscription row exists (creates trial if needed)
        await BillingService.get_or_create_subscription(db, user_id)

        # Default redirect URLs
        if not success_url:
            success_url = "https://pm.fiqros.org/settings?billing=success"
        if not cancel_url:
            cancel_url = "https://pm.fiqros.org/pricing?billing=canceled"

        try:
            if provider == PaymentProvider.STRIPE:
                return await _stripe_create_checkout(
                    customer_email=user_email,
                    success_url=success_url,
                    cancel_url=cancel_url,
                )
            else:
                return await _paddle_create_checkout(
                    customer_email=user_email,
                    success_url=success_url,
                )
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception(
                "Checkout session creation failed for user %s via %s",
                user_id,
                provider.value,
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Payment provider error: {exc}",
            ) from exc

    # -- Customer portal ---------------------------------------------------

    @staticmethod
    async def create_portal_session(
        db: AsyncSession,
        user_id: UUID,
        return_url: str = "",
    ) -> dict:
        """Return a self-serve billing portal URL for the user.

        The portal lets users update their payment methods, view invoices,
        or cancel their subscription without contacting support.

        Raises:
            HTTPException 404: Subscription not found or no provider linked.
            HTTPException 502: Provider API call failed.
        """
        repo = SubscriptionRepository(db)
        subscription = await repo.get_by_user_id(user_id)

        if not subscription or not subscription.provider_customer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active billing relationship found. Complete checkout first.",
            )

        if not return_url:
            return_url = "https://pm.fiqros.org/settings"

        provider = subscription.provider
        customer_id = subscription.provider_customer_id

        try:
            if provider == PaymentProvider.STRIPE:
                portal_url = await _stripe_create_portal(customer_id, return_url)
            else:
                portal_url = await _paddle_get_portal_url(customer_id)

            return {"portal_url": portal_url, "provider": provider.value}
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception(
                "Portal session creation failed for user %s", user_id
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Payment provider error: {exc}",
            ) from exc

    # -- Status query ------------------------------------------------------

    @staticmethod
    async def get_billing_status(
        db: AsyncSession,
        user_id: UUID,
    ) -> dict:
        """Build a high-level billing overview for the frontend.

        Returns a dict matching the ``BillingStatusResponse`` schema.
        """
        subscription = await BillingService.get_or_create_subscription(
            db, user_id
        )

        now = datetime.now(timezone.utc)
        is_trialing = subscription.status == SubscriptionStatus.TRIALING
        is_active = subscription.status in (
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.TRIALING,
        )

        # Auto-expire past-due trials
        if (
            is_trialing
            and subscription.trial_ends_at
            and subscription.trial_ends_at < now
        ):
            repo = SubscriptionRepository(db)
            await repo.update_status(
                subscription.provider_subscription_id or "",
                status=SubscriptionStatus.EXPIRED,
            )
            # Reload after update
            subscription = await repo.get_by_user_id(user_id)
            is_trialing = False
            is_active = False

        return {
            "is_active": is_active,
            "is_trialing": is_trialing,
            "plan_type": subscription.plan_type.value if subscription else PlanType.FREE.value,
            "provider": subscription.provider.value if subscription and subscription.provider else None,
            "trial_ends_at": subscription.trial_ends_at if subscription else None,
            "current_period_end": subscription.current_period_end if subscription else None,
            "subscription": subscription,
        }

    # -- Available providers -----------------------------------------------

    @staticmethod
    def get_available_providers() -> list[dict]:
        """Return a list of configured payment providers for the frontend.

        This lets the pricing page dynamically show only the gateways that
        the deployment has configured.
        """
        providers = []
        if _stripe_configured():
            providers.append({"id": "stripe", "name": "Stripe", "label": "Credit / Debit Card"})
        if _paddle_configured():
            providers.append({"id": "paddle", "name": "Paddle", "label": "Credit / Debit Card (Global)"})
        return providers
