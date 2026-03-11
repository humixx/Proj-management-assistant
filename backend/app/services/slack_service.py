"""Slack helper service: OAuth, list channels, send messages, task sync.

This module provides stateless helpers that accept tokens/credentials
as arguments and wrap Slack API calls using httpx and slack_sdk.
"""
from typing import Any, Dict, List, Optional
import asyncio
import hashlib
import hmac
import logging
import time

import httpx
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

from app.config import settings

logger = logging.getLogger(__name__)

# Status → emoji mapping for Slack message badges
STATUS_EMOJI = {
    "todo": "\U0001f4cb",        # 📋
    "in_progress": "\U0001f6a7", # 🚧
    "review": "\U0001f50d",      # 🔍
    "done": "\u2705",            # ✅
}

PRIORITY_EMOJI = {
    "low": "\U0001f7e2",       # 🟢
    "medium": "\U0001f7e1",    # 🟡
    "high": "\U0001f7e0",      # 🟠
    "critical": "\U0001f534",  # 🔴
}


class SlackService:
    """Stateless Slack service helpers."""

    OAUTH_URL = "https://slack.com/oauth/v2/authorize"
    OAUTH_TOKEN_URL = "https://slack.com/api/oauth.v2.access"

    # Bot scopes needed for posting, listing, auto-joining, and task sync.
    DEFAULT_SCOPES = [
        "channels:read",
        "channels:join",
        "groups:read",
        "chat:write",
        "im:read",
        "mpim:read",
        # Added for task sync features:
        "reactions:read",        # Detect status reactions on task messages
        "users:read",            # Base scope required by users:read.email
        "users:read.email",      # Resolve assignee emails → Slack user IDs
        "channels:history",      # Read message history (needed for reaction events)
    ]

    def build_oauth_url(self, client_id: str, redirect_uri: Optional[str] = None, scopes: Optional[List[str]] = None, state: Optional[str] = None) -> str:
        """Build Slack OAuth v2 authorize URL for a project's app.

        Args:
            client_id: Slack app client ID
            redirect_uri: Redirect URI registered with the app
            scopes: Optional list of scopes; defaults to DEFAULT_SCOPES
            state: Optional state string to include

        Returns:
            URL string to redirect the user to for authorization
        """
        scopes = scopes or self.DEFAULT_SCOPES
        scope_param = ",".join(scopes)
        params: dict = {"client_id": client_id, "scope": scope_param}
        if redirect_uri:
            params["redirect_uri"] = redirect_uri
        if state:
            params["state"] = state

        # Build query string
        encoded = httpx.QueryParams(params)
        return f"{self.OAUTH_URL}?{encoded}"

    async def exchange_code(self, client_id: str, client_secret: str, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange OAuth code for tokens via Slack's oauth.v2.access.

        Returns the parsed JSON response from Slack. Caller should handle
        saving any tokens (bot_token / access_token) and team info.
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            }
            resp = await client.post(self.OAUTH_TOKEN_URL, data=data)
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError:
                logger.exception("Slack oauth exchange failed HTTP")
                raise

            result = resp.json()
            if not result.get("ok"):
                # Return the full payload so callers can inspect error
                logger.warning("Slack oauth exchange returned error: %s", result.get("error"))
            return result

    async def list_channels(self, bot_token: str) -> List[Dict[str, str]]:
        """List channels accessible to the bot token.

        Returns a list of dicts: {id, name}.
        """
        client = AsyncWebClient(token=bot_token)
        channels: List[Dict[str, str]] = []
        cursor: Optional[str] = None

        # types include public and private channels the bot can see
        while True:
            try:
                resp = await client.conversations_list(limit=200, cursor=cursor, types="public_channel,private_channel")
            except SlackApiError as e:
                logger.exception("Slack conversations.list failed: %s", e)
                raise

            if not resp.get("ok"):
                raise Exception(f"Slack API error: {resp.get('error')}")

            for ch in resp.get("channels", []):
                channels.append({"id": ch.get("id"), "name": ch.get("name")})

            cursor = resp.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

            # small throttle to be polite
            await asyncio.sleep(0.1)

        return channels

    async def send_message(self, bot_token: str, channel: str, text: str) -> Dict[str, Any]:
        """Send a message using bot_token to a channel name or id.

        If `channel` looks like an ID (starts with C/G) it will be used as-is.
        Otherwise, the function will try to resolve the channel name to an ID.

        Returns: {success: bool, channel: str, ts: str, error?: str}
        """
        client = AsyncWebClient(token=bot_token)

        # Resolve channel ID if needed
        channel_id = channel
        if not channel.startswith("C") and not channel.startswith("G"):
            # strip leading # if present
            name = channel.lstrip("#")
            try:
                channels = await self.list_channels(bot_token)
            except Exception as e:
                return {"success": False, "error": str(e)}

            match = next((c for c in channels if c.get("name") == name), None)
            if match:
                channel_id = match["id"]
            else:
                # Could not resolve; attempt to send with provided string (may fail)
                logger.info("Could not resolve channel name '%s' to id; attempting API call with provided value", channel)

        try:
            resp = await client.chat_postMessage(channel=channel_id, text=text)
        except SlackApiError as e:
            error_code = e.response.get("error", "") if e.response else ""
            # Auto-join the channel and retry once if bot is not a member
            if error_code == "not_in_channel":
                logger.info("Bot not in channel %s, attempting to join...", channel_id)
                try:
                    await client.conversations_join(channel=channel_id)
                    resp = await client.chat_postMessage(channel=channel_id, text=text)
                except SlackApiError as join_err:
                    logger.exception("Failed to join/send after join for %s: %s", channel_id, join_err)
                    return {"success": False, "error": f"Could not join channel: {join_err}"}
            else:
                logger.exception("Slack chat.postMessage failed: %s", e)
                return {"success": False, "error": str(e)}

        if not resp.get("ok"):
            return {"success": False, "error": resp.get("error")}

        return {"success": True, "channel": resp.get("channel"), "ts": resp.get("ts")}

    # ── Task posting ────────────────────────────────────────────────

    def _build_task_blocks(
        self,
        title: str,
        description: Optional[str],
        status: str,
        priority: str,
        assignee: Optional[str],
        due_date: Optional[str],
        assignee_slack_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Build Slack Block Kit blocks for a task message."""
        status_badge = STATUS_EMOJI.get(status, "") + f" *{status.replace('_', ' ').title()}*"
        priority_badge = PRIORITY_EMOJI.get(priority, "") + f" {priority.title()}"

        # Header
        blocks: List[Dict[str, Any]] = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"📌 {title}", "emoji": True},
            },
        ]

        # Description (truncate if long)
        if description:
            desc_text = description[:300] + ("..." if len(description) > 300 else "")
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": desc_text}})

        # Fields: status, priority, assignee, due date
        fields = [
            {"type": "mrkdwn", "text": f"*Status:* {status_badge}"},
            {"type": "mrkdwn", "text": f"*Priority:* {priority_badge}"},
        ]
        if assignee:
            assignee_display = f"<@{assignee_slack_id}>" if assignee_slack_id else assignee
            fields.append({"type": "mrkdwn", "text": f"*Assignee:* {assignee_display}"})
        if due_date:
            fields.append({"type": "mrkdwn", "text": f"*Due:* {due_date}"})

        blocks.append({"type": "section", "fields": fields})

        # Action buttons for quick status updates
        if task_id:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "actions",
                "block_id": f"task_actions_{task_id}",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "📋 Todo", "emoji": True},
                        "action_id": "task_status_todo",
                        "value": task_id,
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🚧 In Progress", "emoji": True},
                        "action_id": "task_status_in_progress",
                        "value": task_id,
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🔍 Review", "emoji": True},
                        "action_id": "task_status_review",
                        "value": task_id,
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Done", "emoji": True},
                        "action_id": "task_status_done",
                        "style": "primary",
                        "value": task_id,
                    },
                ],
            })

        return blocks

    async def post_task_to_slack(
        self,
        bot_token: str,
        channel: str,
        title: str,
        description: Optional[str] = None,
        status: str = "todo",
        priority: str = "medium",
        assignee: Optional[str] = None,
        due_date: Optional[str] = None,
        assignee_slack_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Post a task to Slack with rich Block Kit formatting and action buttons.

        Returns: {success, channel, ts, error?}
        """
        blocks = self._build_task_blocks(
            title=title,
            description=description,
            status=status,
            priority=priority,
            assignee=assignee,
            due_date=due_date,
            assignee_slack_id=assignee_slack_id,
            task_id=task_id,
        )

        # Fallback text for notifications
        fallback = f"New task: {title}"
        if assignee_slack_id:
            fallback += f" (assigned to <@{assignee_slack_id}>)"

        client = AsyncWebClient(token=bot_token)

        # Resolve channel ID if needed (reuse existing logic)
        channel_id = channel
        if not channel.startswith("C") and not channel.startswith("G"):
            name = channel.lstrip("#")
            try:
                channels = await self.list_channels(bot_token)
            except Exception as e:
                return {"success": False, "error": str(e)}
            match = next((c for c in channels if c.get("name") == name), None)
            if match:
                channel_id = match["id"]

        try:
            resp = await client.chat_postMessage(
                channel=channel_id,
                text=fallback,
                blocks=blocks,
            )
        except SlackApiError as e:
            error_code = e.response.get("error", "") if e.response else ""
            if error_code == "not_in_channel":
                try:
                    await client.conversations_join(channel=channel_id)
                    resp = await client.chat_postMessage(
                        channel=channel_id, text=fallback, blocks=blocks,
                    )
                except SlackApiError as join_err:
                    logger.exception("Failed to join/post task to %s: %s", channel_id, join_err)
                    return {"success": False, "error": str(join_err)}
            else:
                logger.exception("Slack post_task failed: %s", e)
                return {"success": False, "error": str(e)}

        if not resp.get("ok"):
            return {"success": False, "error": resp.get("error")}

        return {
            "success": True,
            "channel": resp.get("channel"),
            "ts": resp.get("ts"),
        }

    async def update_task_message(
        self,
        bot_token: str,
        channel: str,
        ts: str,
        title: str,
        description: Optional[str] = None,
        status: str = "todo",
        priority: str = "medium",
        assignee: Optional[str] = None,
        due_date: Optional[str] = None,
        assignee_slack_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing task message in Slack (e.g. after status change)."""
        blocks = self._build_task_blocks(
            title=title,
            description=description,
            status=status,
            priority=priority,
            assignee=assignee,
            due_date=due_date,
            assignee_slack_id=assignee_slack_id,
            task_id=task_id,
        )

        client = AsyncWebClient(token=bot_token)
        try:
            resp = await client.chat_update(
                channel=channel,
                ts=ts,
                text=f"Task: {title}",
                blocks=blocks,
            )
        except SlackApiError as e:
            logger.exception("Slack chat_update failed: %s", e)
            return {"success": False, "error": str(e)}

        if not resp.get("ok"):
            return {"success": False, "error": resp.get("error")}

        return {"success": True, "channel": resp.get("channel"), "ts": resp.get("ts")}

    # ── User lookup ─────────────────────────────────────────────────

    async def get_user_by_email(self, bot_token: str, email: str) -> Optional[str]:
        """Look up a Slack user ID by email address.

        Requires users:read.email scope. Returns the Slack user ID or None.
        """
        client = AsyncWebClient(token=bot_token)
        try:
            resp = await client.users_lookupByEmail(email=email)
            if resp.get("ok"):
                return resp["user"]["id"]
        except SlackApiError as e:
            error = e.response.get("error", "") if e.response else ""
            if error == "users_not_found":
                logger.info("No Slack user found for email: %s", email)
            else:
                logger.warning("Slack users.lookupByEmail failed: %s", e)
        return None

    async def get_workspace_members(self, bot_token: str) -> List[Dict[str, Any]]:
        """Fetch all (non-bot, non-deleted) members in the Slack workspace.

        Returns list of {id, name, real_name, display_name, email}.
        Requires users:read and users:read.email scopes.
        """
        client = AsyncWebClient(token=bot_token)
        members: List[Dict[str, Any]] = []
        cursor = None

        while True:
            try:
                kwargs: dict = {"limit": 200}
                if cursor:
                    kwargs["cursor"] = cursor

                resp = await client.users_list(**kwargs)
                if not resp.get("ok"):
                    logger.warning("Slack users.list failed: %s", resp.get("error"))
                    break

                for user in resp.get("members", []):
                    if user.get("deleted") or user.get("is_bot") or user.get("id") == "USLACKBOT":
                        continue
                    profile = user.get("profile", {})
                    members.append({
                        "id": user["id"],
                        "name": user.get("name", ""),
                        "real_name": user.get("real_name", profile.get("real_name", "")),
                        "display_name": profile.get("display_name", ""),
                        "email": profile.get("email", ""),
                    })

                cursor = resp.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break
            except SlackApiError as e:
                logger.warning("Slack users.list failed: %s", e)
                break

        return members

    async def find_user_by_name(self, bot_token: str, name: str) -> Optional[str]:
        """Find a Slack user ID by matching name, display_name, or real_name.

        Case-insensitive partial match. Returns the Slack user ID or None.
        """
        members = await self.get_workspace_members(bot_token)
        name_lower = name.lower().strip()

        for member in members:
            if (
                name_lower == member["display_name"].lower()
                or name_lower == member["real_name"].lower()
                or name_lower == member["name"].lower()
                or name_lower in member["real_name"].lower()
                or name_lower in member["display_name"].lower()
            ):
                return member["id"]
        return None

    # ── Webhook signature verification ──────────────────────────────

    @staticmethod
    def verify_signature(signing_secret: str, timestamp: str, body: bytes, signature: str) -> bool:
        """Verify a Slack request signature.

        See: https://api.slack.com/authentication/verifying-requests-from-slack
        """
        # Reject requests older than 5 minutes
        if abs(time.time() - int(timestamp)) > 60 * 5:
            return False

        sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
        computed = "v0=" + hmac.HMAC(
            signing_secret.encode(), sig_basestring.encode(), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(computed, signature)


slack_service = SlackService()
