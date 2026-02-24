"""Slack helper service: OAuth, list channels, send messages.

This module provides stateless helpers that accept tokens/credentials
as arguments and wrap Slack API calls using httpx and slack_sdk.
"""
from typing import Any, Dict, List, Optional
import asyncio
import logging

import httpx
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

from app.config import settings

logger = logging.getLogger(__name__)


class SlackService:
    """Stateless Slack service helpers."""

    OAUTH_URL = "https://slack.com/oauth/v2/authorize"
    OAUTH_TOKEN_URL = "https://slack.com/api/oauth.v2.access"

    # Bot scopes needed for posting, listing, and auto-joining channels.
    DEFAULT_SCOPES = [
        "channels:read",
        "channels:join",
        "groups:read",
        "chat:write",
        "im:read",
        "mpim:read",
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


slack_service = SlackService()
