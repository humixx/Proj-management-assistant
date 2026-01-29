"""Project repository."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Project
from app.db.repositories.base import BaseRepository
from app.schemas import ProjectCreate, ProjectUpdate


class ProjectRepository(BaseRepository):
    """Repository for project operations."""
    
    async def create(self, data: ProjectCreate) -> Project:
        """Create a new project."""
        project = Project(
            name=data.name,
            description=data.description,
            settings=data.settings.model_dump() if data.settings else None,
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project
    
    async def get_by_id(self, project_id: UUID) -> Optional[Project]:
        """Get a project by ID."""
        stmt = select(Project).where(Project.id == project_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> tuple[list[Project], int]:
        """List all projects with pagination."""
        # Get total count
        count_stmt = select(func.count()).select_from(Project)
        total = await self.db.execute(count_stmt)
        total_count = total.scalar() or 0
        
        # Get projects
        stmt = select(Project).offset(skip).limit(limit).order_by(Project.created_at.desc())
        result = await self.db.execute(stmt)
        projects = result.scalars().all()
        
        return list(projects), total_count
    
    async def update(self, project_id: UUID, data: ProjectUpdate) -> Optional[Project]:
        """Update a project."""
        project = await self.get_by_id(project_id)
        if not project:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        if "settings" in update_data and update_data["settings"]:
            update_data["settings"] = update_data["settings"].model_dump() if hasattr(update_data["settings"], "model_dump") else update_data["settings"]
        
        for field, value in update_data.items():
            setattr(project, field, value)
        
        await self.db.commit()
        await self.db.refresh(project)
        return project
    
    async def delete(self, project_id: UUID) -> bool:
        """Delete a project."""
        project = await self.get_by_id(project_id)
        if not project:
            return False
        
        await self.db.delete(project)
        await self.db.commit()
        return True
