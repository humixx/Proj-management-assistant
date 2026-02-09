"""Add users table and user_id to projects

Revision ID: a1b2c3d4e5f6
Revises: 8758f38f0950
Create Date: 2026-02-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '8758f38f0950'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Add user_id column to projects (nullable for existing rows)
    op.add_column('projects', sa.Column('user_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'fk_projects_user_id',
        'projects', 'users',
        ['user_id'], ['id'],
    )
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_projects_user_id', table_name='projects')
    op.drop_constraint('fk_projects_user_id', 'projects', type_='foreignkey')
    op.drop_column('projects', 'user_id')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
