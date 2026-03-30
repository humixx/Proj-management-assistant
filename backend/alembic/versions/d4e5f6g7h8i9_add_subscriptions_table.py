"""Add subscriptions table and payment provider support

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-03-26 23:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Uuid

# revision identifiers, used by Alembic.
revision = 'd4e5f6g7h8i9'
down_revision = 'c3d4e5f6g7h8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    payment_provider_enum = sa.Enum('stripe', 'paddle', name='payment_provider', create_type=True)
    plan_type_enum = sa.Enum('free', 'pro', name='plan_type', create_type=True)
    subscription_status_enum = sa.Enum(
        'trialing', 'active', 'past_due', 'canceled', 'expired',
        name='subscription_status', create_type=True,
    )

    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', Uuid, server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('user_id', Uuid, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        # Provider info
        sa.Column('provider', payment_provider_enum, nullable=True),
        sa.Column('provider_customer_id', sa.String(255), nullable=True, index=True),
        sa.Column('provider_subscription_id', sa.String(255), nullable=True, index=True),
        # Plan details
        sa.Column('plan_type', plan_type_enum, nullable=False, server_default='free'),
        sa.Column('status', subscription_status_enum, nullable=False, server_default='trialing'),
        # Trial tracking
        sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True),
        # Period tracking
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('canceled_at', sa.DateTime(timezone=True), nullable=True),
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('subscriptions')
    # Drop enum types
    sa.Enum(name='subscription_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='plan_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='payment_provider').drop(op.get_bind(), checkfirst=True)
