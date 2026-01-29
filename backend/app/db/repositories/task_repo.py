"""Task repository."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Task
from app.db.repositories.base import BaseRepository
from app.schemas import TaskCreate, TaskUpdate


class TaskRepository(BaseRepository):
    """Repository for task operations."""
    
    async def create(self, project_id: UUID, data: TaskCreate) -> Task:
        """Create a new task."""
        task = Task(
            project_id=project_id,
            title=data.title,
            description=data.description,
            priority=data.priority or "medium",
            assignee=data.assignee,
            due_date=data.due_date,
            tags=data.tags,
            parent_task_id=data.parent_task_id,
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task
    
    async def bulk_create(self, project_id: UUID, tasks: list[TaskCreate]) -> list[Task]:
        """Create multiple tasks at once."""
        created_tasks = []
        for task_data in tasks:
            task = Task(
                project_id=project_id,
                title=task_data.title,
                description=task_data.description,
                priority=task_data.priority or "medium",
                assignee=task_data.assignee,
                due_date=task_data.due_date,
                tags=task_data.tags,
                parent_task_id=task_data.parent_task_id,
            )
            self.db.add(task)
            created_tasks.append(task)
        
        await self.db.commit()
        for task in created_tasks:
            await self.db.refresh(task)
        
        return created_tasks
    
    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        """Get a task by ID."""
        stmt = select(Task).where(Task.id == task_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_by_project(
        self,
        project_id: UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
    ) -> list[Task]:
        """List tasks for a project with optional filters."""
        stmt = select(Task).where(Task.project_id == project_id)
        
        if status:
            stmt = stmt.where(Task.status == status)
        if priority:
            stmt = stmt.where(Task.priority == priority)
        if assignee:
            stmt = stmt.where(Task.assignee == assignee)
        
        stmt = stmt.order_by(Task.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def update(self, task_id: UUID, data: TaskUpdate) -> Optional[Task]:
        """Update a task."""
        task = await self.get_by_id(task_id)
        if not task:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        await self.db.commit()
        await self.db.refresh(task)
        return task
    
    async def delete(self, task_id: UUID) -> bool:
        """Delete a task."""
        task = await self.get_by_id(task_id)
        if not task:
            return False
        
        await self.db.delete(task)
        await self.db.commit()
        return True
