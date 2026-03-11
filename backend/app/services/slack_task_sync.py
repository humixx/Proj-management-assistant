"""Slack ↔ Task synchronisation service.

Orchestrates the outbound (task → Slack) and inbound (Slack → task) flows
by combining SlackService, IntegrationRepository, and TaskRepository.
"""
import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.task import Task
from app.db.repositories.integration_repo import IntegrationRepository
from app.db.repositories.task_repo import TaskRepository
from app.services.slack_service import SlackService

logger = logging.getLogger(__name__)

# Slack reactions → task status mapping
REACTION_STATUS_MAP = {
    "white_check_mark": "done",       # ✅
    "heavy_check_mark": "done",       # ✔️
    "arrows_counterclockwise": "in_progress",  # 🔄
    "construction": "in_progress",     # 🚧
    "memo": "todo",                    # 📝
    "eyes": "review",                  # 👀
    "mag": "review",                   # 🔍
}

# Button action_id → status mapping
ACTION_STATUS_MAP = {
    "task_status_todo": "todo",
    "task_status_in_progress": "in_progress",
    "task_status_review": "review",
    "task_status_done": "done",
}


class SlackTaskSync:
    """Orchestrates task ↔ Slack synchronisation."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.slack = SlackService()
        self.integration_repo = IntegrationRepository(db)
        self.task_repo = TaskRepository(db)

    # ── Outbound: Task → Slack ──────────────────────────────────────

    async def sync_task_to_slack(
        self,
        task: Task,
        project_id: UUID,
    ) -> Optional[str]:
        """Post a task to Slack and return the external_id (channel:ts).

        Returns None if Slack is not configured or posting fails.
        The caller should store the returned external_id on the task.
        """
        integration = await self.integration_repo.get_by_project(project_id)
        if not integration or not integration.bot_token or not integration.channel_id:
            logger.debug("Slack not configured for project %s, skipping sync", project_id)
            return None

        # Try to resolve assignee → Slack user ID for @mention
        assignee_slack_id: Optional[str] = None
        if task.assignee:
            try:
                assignee_clean = task.assignee.lstrip("@").strip()
                if "@" in assignee_clean and "." in assignee_clean:
                    # Looks like an email — try email lookup first
                    assignee_slack_id = await self.slack.get_user_by_email(
                        integration.bot_token, assignee_clean
                    )
                if not assignee_slack_id:
                    # Fall back to name matching
                    assignee_slack_id = await self.slack.find_user_by_name(
                        integration.bot_token, assignee_clean
                    )
                logger.info("Assignee '%s' resolved to Slack ID: %s", task.assignee, assignee_slack_id)
            except Exception:
                logger.exception("Could not resolve assignee: %s", task.assignee)

        result = await self.slack.post_task_to_slack(
            bot_token=integration.bot_token,
            channel=integration.channel_id,
            title=task.title,
            description=task.description,
            status=task.status or "todo",
            priority=task.priority or "medium",
            assignee=task.assignee,
            due_date=str(task.due_date) if task.due_date else None,
            assignee_slack_id=assignee_slack_id,
            task_id=str(task.id),
        )

        if not result.get("success"):
            logger.warning("Failed to post task %s to Slack: %s", task.id, result.get("error"))
            return None

        # Build external_id as "channel:ts" for later lookups
        external_id = f"{result['channel']}:{result['ts']}"
        logger.info("Task %s synced to Slack → %s", task.id, external_id)
        return external_id

    async def sync_tasks_to_slack(
        self,
        tasks: list[Task],
        project_id: UUID,
    ) -> list[Task]:
        """Post multiple tasks to Slack (bulk create flow).

        Updates each task's external_id in the database.
        Returns the list of tasks that were synced.
        """
        synced: list[Task] = []
        for task in tasks:
            external_id = await self.sync_task_to_slack(task, project_id)
            if external_id:
                task.external_id = external_id
                synced.append(task)

        if synced:
            await self.db.commit()
            for t in synced:
                await self.db.refresh(t)

        return synced

    # ── Inbound: Slack → Task ───────────────────────────────────────

    async def handle_status_update(
        self,
        task_id: str,
        new_status: str,
        team_id: str,
    ) -> bool:
        """Update a task's status from a Slack event (button click or reaction).

        Also updates the Slack message to reflect the new status.
        Returns True if successful.
        """
        # Look up integration by team_id (from Slack payload)
        integration = await self.integration_repo.get_by_team_id(team_id)
        if not integration:
            logger.warning("No integration found for team_id %s", team_id)
            return False

        # Get the task
        try:
            task_uuid = UUID(task_id)
        except ValueError:
            logger.warning("Invalid task_id from Slack: %s", task_id)
            return False

        task = await self.task_repo.get_by_id(task_uuid)
        if not task:
            logger.warning("Task %s not found for Slack status update", task_id)
            return False

        # Skip if status is already the same
        if task.status == new_status:
            return True

        # Update task status in DB
        old_status = task.status
        task.status = new_status
        await self.db.commit()
        await self.db.refresh(task)
        logger.info("Task %s status: %s → %s (via Slack)", task_id, old_status, new_status)

        # Update the Slack message to reflect new status
        if task.external_id and integration.bot_token:
            await self._update_slack_message(task, integration.bot_token)

        return True

    async def handle_reaction_event(
        self,
        reaction: str,
        channel: str,
        message_ts: str,
        team_id: str,
    ) -> bool:
        """Handle a reaction_added event from Slack.

        Maps the reaction emoji to a status and updates the task.
        """
        new_status = REACTION_STATUS_MAP.get(reaction)
        if not new_status:
            logger.debug("Ignoring unmapped reaction: %s", reaction)
            return False

        # Find the task by external_id (channel:ts)
        external_id = f"{channel}:{message_ts}"
        task = await self._get_task_by_external_id(external_id, team_id)
        if not task:
            return False

        return await self.handle_status_update(str(task.id), new_status, team_id)

    async def handle_button_action(
        self,
        action_id: str,
        task_id: str,
        team_id: str,
    ) -> bool:
        """Handle a button click from Slack Block Kit interactive message."""
        new_status = ACTION_STATUS_MAP.get(action_id)
        if not new_status:
            logger.warning("Unknown action_id: %s", action_id)
            return False

        return await self.handle_status_update(task_id, new_status, team_id)

    # ── Helpers ─────────────────────────────────────────────────────

    async def _get_task_by_external_id(
        self,
        external_id: str,
        team_id: str,
    ) -> Optional[Task]:
        """Look up a task by its Slack external_id (channel:ts)."""
        integration = await self.integration_repo.get_by_team_id(team_id)
        if not integration:
            return None

        return await self.task_repo.get_by_external_id(
            external_id=external_id,
            project_id=integration.project_id,
        )

    async def _update_slack_message(self, task: Task, bot_token: str) -> None:
        """Update the Slack message for a task to reflect its current state."""
        if not task.external_id:
            return

        try:
            channel, ts = task.external_id.split(":", 1)
        except ValueError:
            logger.warning("Malformed external_id: %s", task.external_id)
            return

        result = await self.slack.update_task_message(
            bot_token=bot_token,
            channel=channel,
            ts=ts,
            title=task.title,
            description=task.description,
            status=task.status or "todo",
            priority=task.priority or "medium",
            assignee=task.assignee,
            due_date=str(task.due_date) if task.due_date else None,
            task_id=str(task.id),
        )

        if not result.get("success"):
            logger.warning("Failed to update Slack message for task %s: %s", task.id, result.get("error"))
