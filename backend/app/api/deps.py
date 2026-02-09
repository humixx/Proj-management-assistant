"""API dependencies."""
from typing import AsyncGenerator
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.

    Yields:
        AsyncSession: Database session
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_project_id(
    x_project_id: str = Header(..., alias="X-Project-ID"),
) -> UUID:
    """
    Dependency that extracts and validates project ID from header.

    Args:
        x_project_id: Project ID from X-Project-ID header

    Returns:
        UUID: Validated project ID

    Raises:
        HTTPException: If header is missing or invalid
    """
    try:
        return UUID(x_project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format",
        )


async def verify_project_ownership(
    project_id: UUID,
    user_id: UUID,
    db: AsyncSession,
) -> None:
    """
    Verify that a project belongs to the given user.

    Raises:
        HTTPException: If project not found or doesn't belong to user
    """
    from app.db.repositories import ProjectRepository
    repo = ProjectRepository(db)
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    # Allow access to orphaned projects (created before auth) — auto-claim them
    if project.user_id is None:
        project.user_id = user_id
        await db.commit()
        await db.refresh(project)
        return

    if project.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project",
        )
