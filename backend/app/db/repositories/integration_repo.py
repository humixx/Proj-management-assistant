"""Integration repository."""
import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.integration import SlackIntegration
from app.db.repositories.base import BaseRepository
from app.utils.encryption import encrypt_api_key, decrypt_api_key

logger = logging.getLogger(__name__)

# Fields that are encrypted at rest in the database.
_ENCRYPTED_FIELDS = {"client_secret", "access_token", "bot_token"}


def _decrypt_integration(integration: Optional[SlackIntegration]) -> Optional[SlackIntegration]:
    """Decrypt sensitive fields in-place so callers get plaintext."""
    if integration is None:
        return None
    for field in _ENCRYPTED_FIELDS:
        value = getattr(integration, field, None)
        if value:
            try:
                setattr(integration, field, decrypt_api_key(value))
            except Exception:
                # Value might be stored in plaintext from before encryption was added.
                # Leave it as-is rather than crashing.
                pass
    return integration


class IntegrationRepository(BaseRepository):
    """Repository for integration operations."""

    def __init__(self, db: AsyncSession):
        """Initialize integration repository."""
        super().__init__(db)

    # ── helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _encrypt_value(value: Optional[str]) -> Optional[str]:
        """Encrypt a single value if it is non-empty."""
        if not value:
            return value
        return encrypt_api_key(value)

    # ── CRUD ────────────────────────────────────────────────────────

    async def create_slack_integration(
        self,
        project_id: UUID,
        client_id: str,
        client_secret: str,
    ) -> SlackIntegration:
        """Create or update a Slack integration with app credentials (before OAuth)."""
        existing = await self.get_by_project(project_id, decrypt=False)
        if existing:
            existing.client_id = client_id
            existing.client_secret = self._encrypt_value(client_secret)
            await self.db.commit()
            await self.db.refresh(existing)
            return _decrypt_integration(existing)  # type: ignore[return-value]

        integration = SlackIntegration(
            project_id=project_id,
            client_id=client_id,
            client_secret=self._encrypt_value(client_secret),
        )
        self.db.add(integration)
        await self.db.commit()
        await self.db.refresh(integration)
        return _decrypt_integration(integration)  # type: ignore[return-value]

    async def get_by_project(
        self,
        project_id: UUID,
        decrypt: bool = True,
    ) -> Optional[SlackIntegration]:
        """Get Slack integration for a project.

        Args:
            project_id: The project UUID.
            decrypt: If True (default), decrypt sensitive fields before returning.
        """
        query = select(SlackIntegration).where(
            SlackIntegration.project_id == project_id
        )
        result = await self.db.execute(query)
        integration = result.scalar_one_or_none()
        if decrypt:
            return _decrypt_integration(integration)
        return integration

    async def update_tokens(
        self,
        project_id: UUID,
        access_token: Optional[str],
        bot_token: Optional[str],
        team_id: Optional[str] = None,
        team_name: Optional[str] = None,
    ) -> Optional[SlackIntegration]:
        """Save OAuth tokens after successful callback."""
        integration = await self.get_by_project(project_id, decrypt=False)
        if not integration:
            integration = SlackIntegration(project_id=project_id)
            self.db.add(integration)

        if access_token is not None:
            integration.access_token = self._encrypt_value(access_token)
        if bot_token is not None:
            integration.bot_token = self._encrypt_value(bot_token)
        if team_id is not None:
            integration.team_id = team_id
        if team_name is not None:
            integration.team_name = team_name

        await self.db.commit()
        await self.db.refresh(integration)
        return _decrypt_integration(integration)

    async def update_slack_integration(
        self,
        project_id: UUID,
        **kwargs,
    ) -> Optional[SlackIntegration]:
        """Update Slack integration fields by project id."""
        integration = await self.get_by_project(project_id, decrypt=False)
        if not integration:
            return None

        for k, v in kwargs.items():
            if hasattr(integration, k):
                # Encrypt sensitive fields
                if k in _ENCRYPTED_FIELDS and v is not None:
                    setattr(integration, k, self._encrypt_value(v))
                else:
                    setattr(integration, k, v)

        await self.db.commit()
        await self.db.refresh(integration)
        return _decrypt_integration(integration)

    async def delete_slack_integration(
        self,
        project_id: UUID
    ) -> bool:
        """Delete Slack integration for a project."""
        integration = await self.get_by_project(project_id, decrypt=False)
        if integration:
            await self.db.delete(integration)
            await self.db.commit()
            return True
        return False
