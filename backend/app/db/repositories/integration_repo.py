"""Integration repository."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.integration import SlackIntegration
from app.db.repositories.base import BaseRepository


class IntegrationRepository(BaseRepository[SlackIntegration]):
    """Repository for integration operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize integration repository."""
        super().__init__(SlackIntegration, db)
    
    async def create_slack_integration(
        self,
        project_id: UUID,
        access_token: str,
        team_id: Optional[str] = None,
        team_name: Optional[str] = None,
        channel_id: Optional[str] = None,
        channel_name: Optional[str] = None
    ) -> SlackIntegration:
        """
        Create a Slack integration.
        
        Args:
            project_id: Project ID
            access_token: Slack access token
            team_id: Slack team ID
            team_name: Slack team name
            channel_id: Slack channel ID
            channel_name: Slack channel name
            
        Returns:
            Created integration
        """
        return await self.create(
            project_id=project_id,
            access_token=access_token,
            team_id=team_id,
            team_name=team_name,
            channel_id=channel_id,
            channel_name=channel_name
        )
    
    async def get_by_project(
        self,
        project_id: UUID
    ) -> Optional[SlackIntegration]:
        """
        Get Slack integration for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Integration or None
        """
        query = select(SlackIntegration).where(
            SlackIntegration.project_id == project_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_slack_integration(
        self,
        integration_id: UUID,
        channel_id: Optional[str] = None,
        channel_name: Optional[str] = None
    ) -> Optional[SlackIntegration]:
        """
        Update Slack integration.
        
        Args:
            integration_id: Integration ID
            channel_id: Slack channel ID
            channel_name: Slack channel name
            
        Returns:
            Updated integration or None
        """
        update_data = {}
        if channel_id is not None:
            update_data["channel_id"] = channel_id
        if channel_name is not None:
            update_data["channel_name"] = channel_name
        
        return await self.update(integration_id, **update_data)
    
    async def delete_slack_integration(
        self,
        project_id: UUID
    ) -> bool:
        """
        Delete Slack integration for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if deleted
        """
        integration = await self.get_by_project(project_id)
        if integration:
            return await self.delete(integration.id)
        return False
