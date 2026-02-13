"""Plan repository."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.plan import Plan
from app.db.repositories.base import BaseRepository


class PlanRepository(BaseRepository):
    """Repository for plan operations."""

    async def create(self, project_id: UUID, goal: str, parent_task_id: UUID, step_order: list[str]) -> Plan:
        """Create a new plan."""
        plan = Plan(
            project_id=project_id,
            parent_task_id=parent_task_id,
            goal=goal,
            step_order=step_order,
        )
        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)
        return plan

    async def get_by_id(self, plan_id: UUID) -> Optional[Plan]:
        """Get a plan by ID."""
        stmt = select(Plan).where(Plan.id == plan_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_parent_task(self, parent_task_id: UUID) -> Optional[Plan]:
        """Get a plan by its parent task ID."""
        stmt = select(Plan).where(Plan.parent_task_id == parent_task_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_project(self, project_id: UUID) -> list[Plan]:
        """Get all plans for a project."""
        stmt = select(Plan).where(Plan.project_id == project_id).order_by(Plan.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_status(self, plan_id: UUID, status: str) -> Optional[Plan]:
        """Update plan status."""
        plan = await self.get_by_id(plan_id)
        if not plan:
            return None
        plan.status = status
        await self.db.commit()
        await self.db.refresh(plan)
        return plan
