"""Slack agent tools — list channels and send messages."""
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.base import BaseTool
from app.db.repositories.integration_repo import IntegrationRepository
from app.services.slack_service import slack_service


class ListSlackChannelsTool(BaseTool):
    """Tool that lists Slack channels for the connected workspace."""

    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id

    @property
    def name(self) -> str:
        return "list_slack_channels"

    @property
    def description(self) -> str:
        return (
            "List Slack channels the bot can access in the connected workspace. "
            "Use this when the user wants to know which channels are available."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    async def execute(self, **kwargs) -> Any:
        repo = IntegrationRepository(self.db)
        integration = await repo.get_by_project(self.project_id)

        if not integration or not integration.bot_token:
            return {"error": "Slack is not connected for this project. Ask the user to set up Slack in Settings > Integrations."}

        try:
            channels = await slack_service.list_channels(integration.bot_token)
        except Exception as e:
            return {"error": f"Failed to list channels: {e}"}

        return {
            "channels": channels,
            "count": len(channels),
            "message": f"Found {len(channels)} channels.",
        }


class SendSlackMessageTool(BaseTool):
    """Tool that sends a message to a Slack channel."""

    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id

    @property
    def name(self) -> str:
        return "send_slack_message"

    @property
    def description(self) -> str:
        return (
            "Send a message to a Slack channel. "
            "If no channel is specified, uses the project's default channel. "
            "The channel can be a name (e.g. 'general') or an ID."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message text to send",
                },
                "channel": {
                    "type": "string",
                    "description": "Channel name or ID. If omitted, uses the project's default channel.",
                },
            },
            "required": ["message"],
        }

    async def execute(self, message: str, channel: str | None = None, **kwargs) -> Any:
        repo = IntegrationRepository(self.db)
        integration = await repo.get_by_project(self.project_id)

        if not integration or not integration.bot_token:
            return {"error": "Slack is not connected for this project. Ask the user to set up Slack in Settings > Integrations."}

        # Resolve channel
        target_channel = channel or integration.channel_name or integration.channel_id
        if not target_channel:
            return {"error": "No channel specified and no default channel set. Ask the user to set a default channel in Settings > Integrations, or specify a channel name."}

        result = await slack_service.send_message(
            bot_token=integration.bot_token,
            channel=target_channel,
            text=message,
        )

        if result["success"]:
            return {"message": f"Message sent to #{target_channel}.", "channel": result["channel"], "ts": result["ts"]}
        else:
            return {"error": f"Failed to send message: {result.get('error', 'unknown error')}"}
