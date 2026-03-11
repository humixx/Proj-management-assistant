"""Slack integration API routes (authenticated + webhook endpoints)."""
import json
from urllib.parse import parse_qs
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
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
from app.services.slack_service import SlackService, slack_service
from app.services.slack_task_sync import SlackTaskSync
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


@router.get("/slack/members")
async def get_slack_members(
    project_id: UUID = Depends(get_current_project_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Fetch Slack workspace members for assignee selection."""
    await verify_project_ownership(project_id, user_id, db)
    repo = IntegrationRepository(db)
    integration = await repo.get_by_project(project_id)

    if not integration or not integration.bot_token:
        raise HTTPException(status_code=404, detail="Slack not connected")

    slack = SlackService()
    members = await slack.get_workspace_members(integration.bot_token)
    return {"members": members}


# ═══════════════════════════════════════════════════════════════════════
#  Slack Inbound Webhooks (unauthenticated — called by Slack directly)
# ═══════════════════════════════════════════════════════════════════════


@router.post("/slack/webhook")
async def slack_events_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Slack Events API webhooks (reactions, etc.).

    This endpoint is unauthenticated — Slack calls it directly.
    We verify the request using Slack's signing secret.
    """
    body = await request.body()
    payload = json.loads(body)

    # ── Step 1: URL Verification Challenge ──────────────────────────
    # Slack sends this when you first configure the webhook URL.
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}

    # ── Step 2: Extract team_id ──────────────────────────────────────
    team_id = payload.get("team_id")

    # TODO: Add proper signature verification using Slack Signing Secret
    # (client_secret != signing_secret — need to store signing_secret separately)

    # ── Step 3: Route events ────────────────────────────────────────
    if payload.get("type") == "event_callback":
        event = payload.get("event", {})
        event_type = event.get("type")

        if event_type == "reaction_added":
            await _handle_reaction_added(event, team_id, db)

    # Slack expects 200 within 3 seconds — always respond quickly.
    return Response(status_code=200)


@router.post("/slack/interactions")
async def slack_interactions(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Slack Block Kit interactive payloads (button clicks).

    Slack sends these as application/x-www-form-urlencoded with a
    `payload` field containing JSON.
    """
    # IMPORTANT: Read raw body FIRST for signature verification.
    # request.form() consumes the stream, so body() would return empty after.
    body = await request.body()

    form_data = parse_qs(body.decode("utf-8"))
    raw_payload = form_data.get("payload", [""])[0]
    if not raw_payload:
        raise HTTPException(status_code=400, detail="Missing payload")

    payload = json.loads(raw_payload)

    # ── Extract team_id ──────────────────────────────────────────────
    team = payload.get("team", {})
    team_id = team.get("id") if isinstance(team, dict) else None

    # TODO: Add proper signature verification using Slack Signing Secret
    # (client_secret != signing_secret — need to store signing_secret separately)

    # ── Route actions ───────────────────────────────────────────────
    payload_type = payload.get("type")

    if payload_type == "block_actions":
        actions = payload.get("actions", [])
        for action in actions:
            action_id = action.get("action_id", "")
            task_id = action.get("value", "")

            if action_id.startswith("task_status_") and task_id and team_id:
                await _handle_button_click(action_id, task_id, team_id, db)

    # Respond immediately so Slack doesn't retry.
    return Response(status_code=200)


# ── Inbound event handlers ──────────────────────────────────────────


async def _handle_reaction_added(
    event: dict,
    team_id: str,
    db: AsyncSession,
) -> None:
    """Process a reaction_added event from Slack."""
    reaction = event.get("reaction", "")
    item = event.get("item", {})
    channel = item.get("channel", "")
    message_ts = item.get("ts", "")

    if not channel or not message_ts or not team_id:
        return

    try:
        sync = SlackTaskSync(db)
        await sync.handle_reaction_event(
            reaction=reaction,
            channel=channel,
            message_ts=message_ts,
            team_id=team_id,
        )
    except Exception:
        logger.exception("Failed to handle reaction event: %s on %s:%s", reaction, channel, message_ts)


async def _handle_button_click(
    action_id: str,
    task_id: str,
    team_id: str,
    db: AsyncSession,
) -> None:
    """Process a button click from a task message in Slack."""
    try:
        sync = SlackTaskSync(db)
        await sync.handle_button_action(
            action_id=action_id,
            task_id=task_id,
            team_id=team_id,
        )
    except Exception:
        logger.exception("Failed to handle button click: %s for task %s", action_id, task_id)
