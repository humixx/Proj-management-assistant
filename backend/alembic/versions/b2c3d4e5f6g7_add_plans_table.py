"""Add plans table and order column to tasks

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add order column to tasks (nullable, only used for plan subtasks)
    op.add_column('tasks', sa.Column('order', sa.Integer(), nullable=True))

    # Create plans table
    op.create_table('plans',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('parent_task_id', sa.UUID(), nullable=False),
        sa.Column('goal', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='active', nullable=False),
        sa.Column('current_step', sa.Integer(), server_default='0', nullable=False),
        sa.Column('step_order', postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('parent_task_id'),
    )
    op.create_index('ix_plans_project_id', 'plans', ['project_id'])


def downgrade() -> None:
    op.drop_index('ix_plans_project_id', table_name='plans')
    op.drop_table('plans')
    op.drop_column('tasks', 'order')
