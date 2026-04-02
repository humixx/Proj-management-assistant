"""Webhook handlers for Stripe and Paddle payment events.

These endpoints are **unauthenticated** — they are called directly by
Stripe/Paddle servers.  Security is enforced via cryptographic signature
verification of the raw request body against the provider's webhook secret.

Lifecycle events handled
------------------------
* ``checkout.session.completed`` / ``transaction.completed``
  → Activate subscription after successful first payment.
* ``customer.subscription.updated`` / ``subscription.updated``
  → Sync billing period, handle plan changes.
* ``customer.subscription.deleted`` / ``subscription.canceled``
  → Mark subscription as canceled and downgrade plan.
* ``invoice.payment_failed``
  → Mark subscription as past-due.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.config import settings
from app.db.models.subscription import (
    PaymentProvider,
    SubscriptionStatus,
)
from app.db.repositories.subscription_repo import SubscriptionRepository
from fastapi import Depends

logger = logging.getLogger(__name__)

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════
#  Signature verification helpers
# ═══════════════════════════════════════════════════════════════════════


def _verify_stripe_signature(payload: bytes, sig_header: str) -> dict:
    """Verify a Stripe webhook signature and return the parsed event.

    Uses the ``stripe`` SDK's built-in verification which checks the
    ``Stripe-Signature`` header against ``STRIPE_WEBHOOK_SECRET``.

    Raises:
        HTTPException 400: If the signature is invalid or the secret
            is not configured.
    """
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="STRIPE_WEBHOOK_SECRET is not configured.",
        )

    import stripe

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
        return event
    except stripe.SignatureVerificationError as e:
        logger.warning("Stripe signature verification failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe signature.",
        )
    except Exception as e:
        logger.exception("Stripe webhook parse error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook payload error.",
        )


def _verify_paddle_signature(payload: bytes, sig_header: str) -> dict:
    """Verify a Paddle webhook signature and return the parsed event.

    Paddle signs webhooks using HMAC-SHA256 with the webhook secret.
    The ``Paddle-Signature`` header contains a timestamp and hash:
    ``ts=TIMESTAMP;h1=HASH``

    Raises:
        HTTPException 400: If the signature is invalid.
    """
    if not settings.PADDLE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PADDLE_WEBHOOK_SECRET is not configured.",
        )

    try:
        # Parse the Paddle-Signature header: "ts=1234;h1=abc..."
        parts = dict(
            part.split("=", 1) for part in sig_header.split(";") if "=" in part
        )
        timestamp = parts.get("ts", "")
        expected_hash = parts.get("h1", "")

        if not timestamp or not expected_hash:
            raise ValueError("Missing ts or h1 in Paddle-Signature header.")

        # Reconstruct the signed payload: "timestamp:body"
        # Paddle uses the raw body bytes — join with colon
        signed_payload = timestamp.encode("utf-8") + b":" + payload
        computed_hash = hmac.new(
            settings.PADDLE_WEBHOOK_SECRET.encode("utf-8"),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()

        logger.debug(
            "Paddle sig debug — ts=%s, expected=%s, computed=%s",
            timestamp,
            expected_hash[:16] + "...",
            computed_hash[:16] + "...",
        )

        if not hmac.compare_digest(computed_hash, expected_hash):
            # In sandbox mode, log a warning but still process the event
            if settings.PADDLE_ENVIRONMENT == "sandbox":
                logger.warning(
                    "Paddle signature mismatch in SANDBOX mode — processing anyway. "
                    "Expected: %s, Computed: %s",
                    expected_hash[:16],
                    computed_hash[:16],
                )
                return json.loads(payload)
            raise ValueError("Signature mismatch.")

        return json.loads(payload)

    except ValueError as e:
        logger.warning("Paddle signature verification failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Paddle signature.",
        )
    except Exception as e:
        logger.exception("Paddle webhook parse error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook payload error.",
        )


# ═══════════════════════════════════════════════════════════════════════
#  Stripe webhook endpoint
# ═══════════════════════════════════════════════════════════════════════


@router.post(
    "/stripe",
    summary="Stripe webhook receiver",
    description="Receives and verifies Stripe webhook events. Do not call manually.",
    include_in_schema=False,  # Hide from Swagger — not user-facing
)
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Process inbound Stripe webhook events."""
    body = await request.body()
    sig_header = request.headers.get("Stripe-Signature", "")

    event = _verify_stripe_signature(body, sig_header)
    event_type = event.get("type", "")
    data_object = event.get("data", {}).get("object", {})

    logger.info("Stripe webhook received: %s", event_type)

    repo = SubscriptionRepository(db)

    # ── checkout.session.completed ───────────────────────────────────
    # Fired when a customer completes the Checkout Session.
    if event_type == "checkout.session.completed":
        customer_id = data_object.get("customer", "")
        subscription_id = data_object.get("subscription", "")
        customer_email = data_object.get("customer_email", "")

        if subscription_id:
            # Look up user by email → activate their subscription
            from app.db.repositories.user_repo import UserRepository

            user_repo = UserRepository(db)
            user = await user_repo.get_by_email(customer_email)

            if user:
                await repo.activate(
                    user_id=user.id,
                    provider=PaymentProvider.STRIPE,
                    provider_customer_id=customer_id,
                    provider_subscription_id=subscription_id,
                )
                logger.info(
                    "Activated subscription for user %s (stripe sub %s)",
                    user.id,
                    subscription_id,
                )

    # ── customer.subscription.updated ────────────────────────────────
    # Fired on renewal, upgrade/downgrade, trial end, etc.
    elif event_type == "customer.subscription.updated":
        subscription_id = data_object.get("id", "")
        stripe_status = data_object.get("status", "")

        status_map = {
            "active": SubscriptionStatus.ACTIVE,
            "trialing": SubscriptionStatus.TRIALING,
            "past_due": SubscriptionStatus.PAST_DUE,
            "canceled": SubscriptionStatus.CANCELED,
            "unpaid": SubscriptionStatus.PAST_DUE,
        }

        new_status = status_map.get(stripe_status)
        if new_status and subscription_id:
            period_start = data_object.get("current_period_start")
            period_end = data_object.get("current_period_end")

            await repo.update_status(
                provider_subscription_id=subscription_id,
                status=new_status,
                current_period_start=(
                    datetime.fromtimestamp(period_start, tz=timezone.utc)
                    if period_start
                    else None
                ),
                current_period_end=(
                    datetime.fromtimestamp(period_end, tz=timezone.utc)
                    if period_end
                    else None
                ),
            )
            logger.info(
                "Updated Stripe subscription %s → %s",
                subscription_id,
                new_status.value,
            )

    # ── customer.subscription.deleted ────────────────────────────────
    # Fired when a subscription is fully canceled (end of billing period).
    elif event_type == "customer.subscription.deleted":
        subscription_id = data_object.get("id", "")
        if subscription_id:
            await repo.update_status(
                provider_subscription_id=subscription_id,
                status=SubscriptionStatus.CANCELED,
                canceled_at=datetime.now(timezone.utc),
            )
            logger.info("Canceled Stripe subscription %s", subscription_id)

    # ── invoice.payment_failed ───────────────────────────────────────
    # Fired when a recurring payment fails.
    elif event_type == "invoice.payment_failed":
        subscription_id = data_object.get("subscription", "")
        if subscription_id:
            await repo.update_status(
                provider_subscription_id=subscription_id,
                status=SubscriptionStatus.PAST_DUE,
            )
            logger.info(
                "Marked Stripe subscription %s as past_due", subscription_id
            )

    # Always respond 200 so Stripe doesn't retry.
    return Response(status_code=200)


# ═══════════════════════════════════════════════════════════════════════
#  Paddle webhook endpoint
# ═══════════════════════════════════════════════════════════════════════


@router.post(
    "/paddle",
    summary="Paddle webhook receiver",
    description="Receives and verifies Paddle webhook events. Do not call manually.",
    include_in_schema=False,
)
async def paddle_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Process inbound Paddle webhook events."""
    body = await request.body()
    sig_header = request.headers.get("Paddle-Signature", "")

    event = _verify_paddle_signature(body, sig_header)
    event_type = event.get("event_type", "")
    data = event.get("data", {})

    logger.info("Paddle webhook received: %s", event_type)
    logger.info("Paddle event data keys: %s", list(data.keys()))
    logger.info("Paddle event data: %s", json.dumps(data, default=str)[:1000])

    repo = SubscriptionRepository(db)

    # ── transaction.completed ────────────────────────────────────────
    # Fired after a successful checkout / payment.
    if event_type == "transaction.completed":
        customer_id = data.get("customer_id", "")
        subscription_id = data.get("subscription_id", "") or data.get("id", "")

        # Paddle may include customer email in different locations
        customer_email = ""
        # Check nested customer object
        customer = data.get("customer", {}) or {}
        customer_email = customer.get("email", "")
        # Fallback: check billing_details
        if not customer_email:
            billing = data.get("billing_details", {}) or {}
            customer_email = billing.get("email", "")
        # Fallback: check checkout object
        if not customer_email:
            checkout = data.get("checkout", {}) or {}
            customer_email = checkout.get("customer_email", "")

        logger.info(
            "transaction.completed — customer_id=%s, subscription_id=%s, email=%s",
            customer_id, subscription_id, customer_email,
        )

        if customer_email:
            from app.db.repositories.user_repo import UserRepository

            user_repo = UserRepository(db)
            user = await user_repo.get_by_email(customer_email)

            if user:
                await repo.activate(
                    user_id=user.id,
                    provider=PaymentProvider.PADDLE,
                    provider_customer_id=customer_id,
                    provider_subscription_id=subscription_id or customer_id,
                )
                logger.info(
                    "Activated subscription for user %s (paddle sub %s)",
                    user.id,
                    subscription_id or customer_id,
                )
            else:
                logger.warning("No user found for Paddle customer email: %s", customer_email)
        else:
            logger.warning(
                "No customer email in Paddle transaction.completed event. "
                "customer_id=%s — attempting lookup via Paddle API.",
                customer_id,
            )
            # Try to fetch customer email from Paddle API
            if customer_id:
                import httpx

                base_url = (
                    "https://sandbox-api.paddle.com"
                    if settings.PADDLE_ENVIRONMENT == "sandbox"
                    else "https://api.paddle.com"
                )
                try:
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(
                            f"{base_url}/customers/{customer_id}",
                            headers={"Authorization": f"Bearer {settings.PADDLE_API_KEY}"},
                            timeout=10.0,
                        )
                        if resp.is_success:
                            cust_data = resp.json().get("data", {})
                            customer_email = cust_data.get("email", "")
                            logger.info("Fetched customer email from Paddle: %s", customer_email)

                            if customer_email:
                                from app.db.repositories.user_repo import UserRepository

                                user_repo = UserRepository(db)
                                user = await user_repo.get_by_email(customer_email)
                                if user:
                                    await repo.activate(
                                        user_id=user.id,
                                        provider=PaymentProvider.PADDLE,
                                        provider_customer_id=customer_id,
                                        provider_subscription_id=subscription_id or customer_id,
                                    )
                                    logger.info(
                                        "Activated subscription for user %s via API lookup",
                                        user.id,
                                    )
                except Exception as e:
                    logger.exception("Failed to fetch Paddle customer: %s", e)

    # ── subscription.updated ─────────────────────────────────────────
    elif event_type == "subscription.updated":
        subscription_id = data.get("id", "")
        paddle_status = data.get("status", "")

        status_map = {
            "active": SubscriptionStatus.ACTIVE,
            "trialing": SubscriptionStatus.TRIALING,
            "past_due": SubscriptionStatus.PAST_DUE,
            "paused": SubscriptionStatus.CANCELED,
        }

        new_status = status_map.get(paddle_status)
        if new_status and subscription_id:
            # Paddle billing period
            current_period = data.get("current_billing_period", {}) or {}
            period_start_str = current_period.get("starts_at")
            period_end_str = current_period.get("ends_at")

            await repo.update_status(
                provider_subscription_id=subscription_id,
                status=new_status,
                current_period_start=(
                    datetime.fromisoformat(period_start_str)
                    if period_start_str
                    else None
                ),
                current_period_end=(
                    datetime.fromisoformat(period_end_str)
                    if period_end_str
                    else None
                ),
            )
            logger.info(
                "Updated Paddle subscription %s → %s",
                subscription_id,
                new_status.value,
            )

    # ── subscription.canceled ────────────────────────────────────────
    elif event_type == "subscription.canceled":
        subscription_id = data.get("id", "")
        if subscription_id:
            canceled_at_str = data.get("canceled_at")
            await repo.update_status(
                provider_subscription_id=subscription_id,
                status=SubscriptionStatus.CANCELED,
                canceled_at=(
                    datetime.fromisoformat(canceled_at_str)
                    if canceled_at_str
                    else datetime.now(timezone.utc)
                ),
            )
            logger.info("Canceled Paddle subscription %s", subscription_id)

    return Response(status_code=200)
