"""Billing and subscription schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SubscriptionResponse(BaseModel):
    """Schema returned when querying a user's current subscription state."""
    id: UUID
    provider: Optional[str] = None
    provider_customer_id: Optional[str] = None
    plan_type: str = "free"
    status: str = "trialing"
    trial_ends_at: Optional[datetime] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckoutRequest(BaseModel):
    """Schema for initiating a checkout session."""
    provider: str  # "stripe" or "paddle"
    plan: str = "pro"
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CheckoutResponse(BaseModel):
    """Schema returned after creating a checkout session."""
    checkout_url: str
    session_id: Optional[str] = None
    provider: str


class CustomerPortalResponse(BaseModel):
    """Schema returned with a link to the billing management portal."""
    portal_url: str
    provider: str


class BillingStatusResponse(BaseModel):
    """High-level billing overview for the frontend UI."""
    is_active: bool
    is_trialing: bool
    plan_type: str
    provider: Optional[str] = None
    trial_ends_at: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    subscription: Optional[SubscriptionResponse] = None
