"""Subscription model for payment/billing integration."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
import enum

from app.db.database import Base


class SubscriptionStatus(str, enum.Enum):
    """Possible states of a user subscription."""
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"


class PaymentProvider(str, enum.Enum):
    """Supported payment gateway providers."""
    STRIPE = "stripe"
    PADDLE = "paddle"


class PlanType(str, enum.Enum):
    """Subscription plan tiers."""
    FREE = "free"
    PRO = "pro"


class Subscription(Base):
    """Tracks a user's subscription and payment provider details.
    
    This model is provider-agnostic: it stores identifiers for both
    Stripe and Paddle so that users can pay through either gateway.
    """

    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Provider info
    provider = Column(
        SAEnum(PaymentProvider, name="payment_provider", create_constraint=True, values_callable=lambda e: [x.value for x in e]),
        nullable=True,
    )
    provider_customer_id = Column(String(255), nullable=True, index=True)
    provider_subscription_id = Column(String(255), nullable=True, index=True)

    # Plan details
    plan_type = Column(
        SAEnum(PlanType, name="plan_type", create_constraint=True, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        server_default="free",
    )
    status = Column(
        SAEnum(SubscriptionStatus, name="subscription_status", create_constraint=True, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        server_default="trialing",
    )

    # Trial tracking
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="subscription")
