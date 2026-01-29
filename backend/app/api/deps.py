# Dependency injection (DB sessions, etc.)
from typing import AsyncGenerator
from uuid import UUID

from fastapi import Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db as _get_db


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency.
    
    Yields:
        AsyncSession: Database session
    """
    async for session in _get_db():
        yield session


async def get_current_project_id(
    x_project_id: str = Header(..., description="Project ID")
) -> UUID:
    """
    Extract and validate project ID from request header.
    
    Args:
        x_project_id: Project ID from X-Project-ID header
        
    Returns:
        UUID: Validated project ID
        
    Raises:
        HTTPException: If project ID is missing or invalid
    """
    try:
        return UUID(x_project_id)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid or missing X-Project-ID header"
        )

