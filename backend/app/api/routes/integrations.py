"""Slack integration API routes."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_project_id, verify_project_ownership
from app.auth.deps import get_current_user_id
from app.db.repositories.integration_repo import IntegrationRepository
from app.schemas import (
    SlackSetupRequest,
    SlackConnectRequest,
    SlackOAuthURLResponse,
    SlackSetDefaultChannelRequest,
    SlackChannel,
    SlackChannelList,
    SlackIntegrationResponse,
    SlackMessageRequest,
    SlackMessageResponse,
)
from app.services.slack_service import slack_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def _build_response(integration) -> dict:
    """Build a standardised SlackIntegrationResponse dict."""
    has_credentials = bool(integration.client_id and integration.client_secret)
    connected = bool(integration.bot_token or integration.access_token)
    return {
        "id": integration.id,
        "has_credentials": has_credentials,
        "connected": connected,
        "team_name": integration.team_name,
        "channel_id": integration.channel_id,
        "channel_name": integration.channel_name,
        "created_at": integration.created_at,
    }


@router.post("/slack/setup", response_model=SlackOAuthURLResponse)
async def setup_slack(
    data: SlackSetupRequest,
    project_id: UUID = Depends(get_current_project_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Save Slack app credentials and return the OAuth URL."""
    await verify_project_ownership(project_id, user_id, db)
    repo = IntegrationRepository(db)

    # Upsert: update if exists, create if not
    existing = await repo.get_by_project(project_id)
    if existing:
        await repo.update_slack_integration(
            project_id,
            client_id=data.client_id,
            client_secret=data.client_secret,
            # Clear old tokens when re-configuring credentials
            access_token=None,
            bot_token=None,
            team_id=None,
            team_name=None,
        )
    else:
        await repo.create_slack_integration(
            project_id=project_id,
            client_id=data.client_id,
            client_secret=data.client_secret,
        )

    # Build OAuth URL (frontend will append its own redirect_uri)
    oauth_url = slack_service.build_oauth_url(data.client_id)
    return {"oauth_url": oauth_url, "message": "Credentials saved. Connect to Slack to complete setup."}


@router.post("/slack/callback", response_model=SlackIntegrationResponse)
async def slack_callback(
    data: SlackConnectRequest,
    project_id: UUID = Depends(get_current_project_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Exchange OAuth code for tokens."""
    await verify_project_ownership(project_id, user_id, db)
    repo = IntegrationRepository(db)
    integration = await repo.get_by_project(project_id)

    if not integration or not integration.client_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Set up credentials first")

    logger.info("Slack callback received for project %s: code=%s redirect_uri=%s client_id=%s",
                project_id, data.code, data.redirect_uri,
                (integration.client_id[:8] + "...") if integration.client_id else None)

    try:
        tokens = await slack_service.exchange_code(
            client_id=integration.client_id,
            client_secret=integration.client_secret,
            code=data.code,
            redirect_uri=data.redirect_uri,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"OAuth exchange failed: {e}")

    # Slack OAuth v2: the top-level `access_token` IS the bot token (xoxb-...).
    # There is no separate `bot_token` key in the response.
    bot_token = tokens.get("access_token")
    team_data = tokens.get("team") or {}

    updated = await repo.update_tokens(
        project_id=project_id,
        access_token=bot_token,
        bot_token=bot_token,
        team_id=team_data.get("id") if isinstance(team_data, dict) else None,
        team_name=team_data.get("name") if isinstance(team_data, dict) else None,
    )
    return _build_response(updated)


@router.get("/slack/status", response_model=SlackIntegrationResponse)
async def get_slack_status(
    project_id: UUID = Depends(get_current_project_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get Slack integration status for the current project."""
    await verify_project_ownership(project_id, user_id, db)
    repo = IntegrationRepository(db)
    integration = await repo.get_by_project(project_id)

    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Slack integration for this project")

    return _build_response(integration)


@router.get("/slack/channels", response_model=SlackChannelList)
async def list_channels(
    project_id: UUID = Depends(get_current_project_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List Slack channels for the connected workspace."""
    await verify_project_ownership(project_id, user_id, db)
    repo = IntegrationRepository(db)
    integration = await repo.get_by_project(project_id)

    if not integration or not integration.bot_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slack not connected")

    try:
        channels = await slack_service.list_channels(integration.bot_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Slack API error: {e}")

    return {"channels": channels}


@router.put("/slack/channel", response_model=SlackIntegrationResponse)
async def set_default_channel(
    data: SlackSetDefaultChannelRequest,
    project_id: UUID = Depends(get_current_project_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Set the default Slack channel for the project."""
    await verify_project_ownership(project_id, user_id, db)
    repo = IntegrationRepository(db)
    integration = await repo.get_by_project(project_id)

    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Slack integration")

    updated = await repo.update_slack_integration(
        project_id,
        channel_id=data.channel_id,
        channel_name=data.channel_name,
    )
    return _build_response(updated)


@router.post("/slack/send", response_model=SlackMessageResponse)
async def send_message(
    data: SlackMessageRequest,
    project_id: UUID = Depends(get_current_project_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Send a message to a Slack channel."""
    await verify_project_ownership(project_id, user_id, db)
    repo = IntegrationRepository(db)
    integration = await repo.get_by_project(project_id)

    if not integration or not integration.bot_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slack not connected")

    result = await slack_service.send_message(
        bot_token=integration.bot_token,
        channel=data.channel,
        text=data.message,
    )

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=result.get("error", "Failed to send"))

    return {"success": True, "ts": result.get("ts"), "channel": result.get("channel")}


@router.delete("/slack")
async def disconnect_slack(
    project_id: UUID = Depends(get_current_project_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect Slack integration for the project."""
    await verify_project_ownership(project_id, user_id, db)
    repo = IntegrationRepository(db)
    deleted = await repo.delete_slack_integration(project_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Slack integration to remove")

    return {"message": "Slack integration removed"}
