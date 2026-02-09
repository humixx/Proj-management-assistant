"""Task API routes."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_project_id, verify_project_ownership
from app.auth.deps import get_current_user
from app.db.models.user import User
from app.db.repositories import TaskRepository
from app.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    BulkTaskCreate,
    BulkTaskResponse,
)

router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    project_id: UUID = Depends(get_current_project_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new task."""
    await verify_project_ownership(project_id, current_user.id, db)
    repo = TaskRepository(db)
    task = await repo.create(project_id, data)
    return task


@router.post("/bulk", response_model=BulkTaskResponse, status_code=status.HTTP_201_CREATED)
async def bulk_create_tasks(
    data: BulkTaskCreate,
    project_id: UUID = Depends(get_current_project_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create multiple tasks at once."""
    await verify_project_ownership(project_id, current_user.id, db)
    repo = TaskRepository(db)
    tasks = await repo.bulk_create(project_id, data.tasks)
    return BulkTaskResponse(created=tasks, count=len(tasks))


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    project_id: UUID = Depends(get_current_project_id),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List tasks with optional filters."""
    await verify_project_ownership(project_id, current_user.id, db)
    repo = TaskRepository(db)
    tasks = await repo.list_by_project(
        project_id,
        status=status,
        priority=priority,
        assignee=assignee,
    )
    return TaskListResponse(tasks=tasks, total=len(tasks))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a task by ID."""
    repo = TaskRepository(db)
    task = await repo.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    await verify_project_ownership(task.project_id, current_user.id, db)
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a task."""
    repo = TaskRepository(db)
    task = await repo.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    await verify_project_ownership(task.project_id, current_user.id, db)
    task = await repo.update(task_id, data)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a task."""
    repo = TaskRepository(db)
    task = await repo.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    await verify_project_ownership(task.project_id, current_user.id, db)
    await repo.delete(task_id)
