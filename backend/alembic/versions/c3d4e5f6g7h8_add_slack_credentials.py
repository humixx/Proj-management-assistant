"""Add Slack credentials columns

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-02-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c3d4e5f6g7h8'
down_revision = 'b2c3d4e5f6g7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add per-project Slack app credentials
    op.add_column('slack_integrations', sa.Column('client_id', sa.String(255), nullable=True))
    op.add_column('slack_integrations', sa.Column('client_secret', sa.String(500), nullable=True))
    op.add_column('slack_integrations', sa.Column('bot_token', sa.String(500), nullable=True))

    # Make access_token nullable (row exists before OAuth completes)
    op.alter_column('slack_integrations', 'access_token', existing_type=sa.String(500), nullable=True)


def downgrade() -> None:
    op.alter_column('slack_integrations', 'access_token', existing_type=sa.String(500), nullable=False)
    op.drop_column('slack_integrations', 'bot_token')
    op.drop_column('slack_integrations', 'client_secret')
    op.drop_column('slack_integrations', 'client_id')
