"""Billing API routes.

Provides authenticated endpoints for:
* Creating checkout sessions (Stripe / Paddle)
* Accessing the customer self-serve portal
* Querying current subscription / trial status
* Listing available payment providers
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.auth.deps import get_current_user, get_current_user_id
from app.db.models.subscription import PaymentProvider
from app.db.models.user import User
from app.schemas.billing import (
    BillingStatusResponse,
    CheckoutRequest,
    CheckoutResponse,
    CustomerPortalResponse,
)
from app.services.billing_service import BillingService

logger = logging.getLogger(__name__)

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════
#  Checkout
# ═══════════════════════════════════════════════════════════════════════


@router.post(
    "/checkout",
    response_model=CheckoutResponse,
    summary="Create a checkout session",
    description=(
        "Initialise a checkout session with the chosen payment provider. "
        "Returns a URL that the frontend should redirect the user to."
    ),
)
async def create_checkout(
    body: CheckoutRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a checkout session for the authenticated user."""
    try:
        provider = PaymentProvider(body.provider)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider '{body.provider}'. Use 'stripe' or 'paddle'.",
        )

    result = await BillingService.create_checkout_session(
        db=db,
        user_id=user.id,
        user_email=user.email,
        provider=provider,
        success_url=body.success_url or "",
        cancel_url=body.cancel_url or "",
    )

    logger.info(
        "Checkout session created for user %s via %s",
        user.id,
        provider.value,
    )
    return result


# ═══════════════════════════════════════════════════════════════════════
#  Customer portal
# ═══════════════════════════════════════════════════════════════════════


@router.post(
    "/portal",
    response_model=CustomerPortalResponse,
    summary="Open billing portal",
    description=(
        "Returns a URL to the self-serve billing portal where the user "
        "can update payment methods, view invoices, or cancel."
    ),
)
async def create_portal_session(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a customer portal session for the authenticated user."""
    result = await BillingService.create_portal_session(
        db=db,
        user_id=user.id,
    )

    logger.info(
        "Portal session created for user %s via %s",
        user.id,
        result["provider"],
    )
    return result


# ═══════════════════════════════════════════════════════════════════════
#  Subscription status
# ═══════════════════════════════════════════════════════════════════════


@router.get(
    "/status",
    response_model=BillingStatusResponse,
    summary="Get billing status",
    description=(
        "Returns the authenticated user's current subscription state, "
        "including trial expiration, active plan, and provider details."
    ),
)
async def get_billing_status(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the current billing/subscription status."""
    return await BillingService.get_billing_status(db=db, user_id=user_id)


# ═══════════════════════════════════════════════════════════════════════
#  Available providers
# ═══════════════════════════════════════════════════════════════════════


@router.get(
    "/providers",
    summary="List available payment providers",
    description=(
        "Returns which payment gateways are configured on this deployment. "
        "The frontend pricing page uses this to show the correct options."
    ),
)
async def list_providers():
    """List payment providers that have been configured in .env."""
    providers = BillingService.get_available_providers()
    return {"providers": providers}
