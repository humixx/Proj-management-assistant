"""Subscription repository for billing operations."""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db.models.subscription import (
    Subscription,
    SubscriptionStatus,
    PaymentProvider,
    PlanType,
)
from app.db.repositories.base import BaseRepository


# Default trial duration
TRIAL_DURATION_DAYS = 7


class SubscriptionRepository(BaseRepository):
    """Repository for subscription CRUD and query operations."""

    async def get_by_user_id(self, user_id: UUID) -> Optional[Subscription]:
        """Retrieve a subscription by its owning user ID.

        Args:
            user_id: UUID of the user.

        Returns:
            The Subscription row, or None if the user has no subscription.
        """
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_provider_customer_id(
        self, provider_customer_id: str
    ) -> Optional[Subscription]:
        """Look up a subscription by the external provider customer ID.

        Useful inside webhook handlers where we only receive the
        provider's own customer identifier.
        """
        stmt = select(Subscription).where(
            Subscription.provider_customer_id == provider_customer_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_provider_subscription_id(
        self, provider_subscription_id: str
    ) -> Optional[Subscription]:
        """Look up a subscription by the external provider subscription ID.

        Primary lookup path for webhook events like
        ``subscription.updated`` or ``subscription.canceled``.
        """
        stmt = select(Subscription).where(
            Subscription.provider_subscription_id == provider_subscription_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_trial(self, user_id: UUID) -> Subscription:
        """Provision a new subscription in *trialing* state.

        Called once per user, typically during registration or on
        first visit to the billing page.

        Args:
            user_id: UUID of the user to create the trial for.

        Returns:
            The newly created Subscription row.
        """
        now = datetime.now(timezone.utc)
        subscription = Subscription(
            user_id=user_id,
            plan_type=PlanType.PRO,
            status=SubscriptionStatus.TRIALING,
            trial_ends_at=now + timedelta(days=TRIAL_DURATION_DAYS),
        )
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def activate(
        self,
        user_id: UUID,
        *,
        provider: PaymentProvider,
        provider_customer_id: str,
        provider_subscription_id: str,
        current_period_start: Optional[datetime] = None,
        current_period_end: Optional[datetime] = None,
    ) -> Subscription:
        """Transition a subscription to *active* after successful checkout.

        Args:
            user_id: UUID of the user.
            provider: Which payment gateway processed the charge.
            provider_customer_id: Customer ID from Stripe/Paddle.
            provider_subscription_id: Subscription ID from Stripe/Paddle.
            current_period_start: Billing period start timestamp.
            current_period_end: Billing period end timestamp.

        Returns:
            The updated Subscription row.
        """
        subscription = await self.get_by_user_id(user_id)
        if not subscription:
            subscription = Subscription(user_id=user_id)
            self.db.add(subscription)

        subscription.provider = provider
        subscription.provider_customer_id = provider_customer_id
        subscription.provider_subscription_id = provider_subscription_id
        subscription.plan_type = PlanType.PRO
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.current_period_start = current_period_start
        subscription.current_period_end = current_period_end
        subscription.canceled_at = None

        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def update_status(
        self,
        provider_subscription_id: str,
        *,
        status: SubscriptionStatus,
        current_period_start: Optional[datetime] = None,
        current_period_end: Optional[datetime] = None,
        canceled_at: Optional[datetime] = None,
    ) -> Optional[Subscription]:
        """Update subscription status — called by webhook handlers.

        Args:
            provider_subscription_id: The external subscription ID.
            status: New status to set.
            current_period_start: Updated billing period start.
            current_period_end: Updated billing period end.
            canceled_at: When the subscription was canceled (if applicable).

        Returns:
            The updated Subscription, or None if not found.
        """
        subscription = await self.get_by_provider_subscription_id(
            provider_subscription_id
        )
        if not subscription:
            return None

        subscription.status = status
        if current_period_start is not None:
            subscription.current_period_start = current_period_start
        if current_period_end is not None:
            subscription.current_period_end = current_period_end
        if canceled_at is not None:
            subscription.canceled_at = canceled_at

        # Downgrade plan when subscription is no longer active
        if status in (SubscriptionStatus.CANCELED, SubscriptionStatus.EXPIRED):
            subscription.plan_type = PlanType.FREE

        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription
