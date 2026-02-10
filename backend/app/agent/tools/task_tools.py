"""Task management tools for the agent."""
from typing import Any, AsyncGenerator, Optional
from uuid import UUID
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.base import BaseTool
from app.db.repositories import TaskRepository
from app.schemas import TaskCreate, TaskUpdate


class CreateTaskTool(BaseTool):
    """Tool for creating a single task. Kept for backward compat but not registered."""

    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id

    @property
    def name(self) -> str:
        return "create_task"

    @property
    def description(self) -> str:
        return """Create a new task in the project. Use for adding a single task.
        For multiple tasks, use bulk_create_tasks instead."""

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Clear, actionable task title",
                },
                "description": {
                    "type": "string",
                    "description": "Detailed description of what needs to be done",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "Task priority (default: medium)",
                },
                "assignee": {
                    "type": "string",
                    "description": "Person assigned to the task",
                },
                "due_date": {
                    "type": "string",
                    "description": "Due date in YYYY-MM-DD format",
                },
            },
            "required": ["title"],
        }

    async def execute(
        self,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        assignee: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> Any:
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = date.fromisoformat(due_date)
            except ValueError:
                pass

        task_data = TaskCreate(
            title=title,
            description=description,
            priority=priority,
            assignee=assignee,
            due_date=parsed_due_date,
        )

        repo = TaskRepository(self.db)
        task = await repo.create(self.project_id, task_data)

        return {
            "success": True,
            "message": f"Task '{title}' created successfully.",
            "task": {
                "id": str(task.id),
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
            },
        }


class BulkCreateTasksTool(BaseTool):
    """Tool for creating multiple tasks at once. Kept for backward compat but not registered."""

    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id

    @property
    def name(self) -> str:
        return "bulk_create_tasks"

    @property
    def description(self) -> str:
        return """Create multiple tasks at once. Use this when generating a task list
        from requirements or creating several related tasks."""

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "description": "List of tasks to create",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                            "assignee": {"type": "string"},
                        },
                        "required": ["title"],
                    },
                },
            },
            "required": ["tasks"],
        }

    async def execute(self, tasks: list[dict]) -> Any:
        task_creates = []
        for t in tasks:
            task_creates.append(TaskCreate(
                title=t["title"],
                description=t.get("description"),
                priority=t.get("priority", "medium"),
                assignee=t.get("assignee"),
            ))

        repo = TaskRepository(self.db)
        created_tasks = await repo.bulk_create(self.project_id, task_creates)

        return {
            "success": True,
            "message": f"Created {len(created_tasks)} tasks successfully.",
            "count": len(created_tasks),
            "tasks": [
                {"id": str(t.id), "title": t.title, "priority": t.priority}
                for t in created_tasks
            ],
        }


class ListTasksTool(BaseTool):
    """Tool for listing tasks."""

    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id

    @property
    def name(self) -> str:
        return "list_tasks"

    @property
    def description(self) -> str:
        return """List all tasks in the project with optional filters.
        Use to see current tasks, their status, and priorities.
        Returns task IDs which can be used with update_task and delete_task."""

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["todo", "in_progress", "review", "done"],
                    "description": "Filter by status",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "Filter by priority",
                },
            },
        }

    async def execute(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> Any:
        repo = TaskRepository(self.db)
        tasks = await repo.list_by_project(
            self.project_id,
            status=status,
            priority=priority,
        )

        if not tasks:
            return {
                "found": False,
                "message": "No tasks found.",
                "tasks": [],
            }

        return {
            "found": True,
            "message": f"Found {len(tasks)} tasks.",
            "tasks": [
                {
                    "id": str(t.id),
                    "title": t.title,
                    "status": t.status,
                    "priority": t.priority,
                    "assignee": t.assignee,
                    "due_date": str(t.due_date) if t.due_date else None,
                }
                for t in tasks
            ],
        }


class ProposeTasksTool(BaseTool):
    """Tool for proposing tasks for user approval. Does NOT create tasks in the database."""

    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id

    @property
    def name(self) -> str:
        return "propose_tasks"

    @property
    def description(self) -> str:
        return """Propose tasks for the user to review and approve before creation.
        Tasks are NOT created in the database until the user explicitly approves them.
        Always use this instead of directly creating tasks. After user approval,
        use confirm_proposed_tasks to actually create them."""

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "description": "List of tasks to propose for approval",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Clear, actionable task title",
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description of what needs to be done",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                                "description": "Task priority (default: medium)",
                            },
                            "assignee": {
                                "type": "string",
                                "description": "Person assigned to the task",
                            },
                            "due_date": {
                                "type": "string",
                                "description": "Due date in YYYY-MM-DD format",
                            },
                        },
                        "required": ["title"],
                    },
                },
            },
            "required": ["tasks"],
        }

    async def execute(self, tasks: list[dict]) -> Any:
        proposed = []
        for i, t in enumerate(tasks):
            proposed.append({
                "temp_id": f"t{i + 1}",
                "title": t["title"],
                "description": t.get("description"),
                "priority": t.get("priority", "medium"),
                "assignee": t.get("assignee"),
                "due_date": t.get("due_date"),
            })

        return {
            "type": "proposal",
            "message": f"Proposed {len(proposed)} task(s) for your approval. These tasks have NOT been created yet. When the user approves, you MUST call confirm_proposed_tasks with these exact tasks to actually create them.",
            "tasks": proposed,
        }


class ConfirmProposedTasksTool(BaseTool):
    """Tool for creating tasks after user approval."""

    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id

    @property
    def name(self) -> str:
        return "confirm_proposed_tasks"

    @property
    def description(self) -> str:
        return """Create tasks that were previously proposed and approved by the user.
        Only call this AFTER the user has explicitly approved the proposed tasks.
        Never call this without prior user approval."""

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "description": "List of approved tasks to create",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                            },
                            "assignee": {"type": "string"},
                            "due_date": {"type": "string"},
                        },
                        "required": ["title"],
                    },
                },
            },
            "required": ["tasks"],
        }

    @property
    def supports_streaming(self) -> bool:
        return True

    async def execute(self, tasks: list[dict]) -> Any:
        """Non-streaming fallback — creates all tasks at once."""
        result: Any = None
        async for event in self.execute_streaming(tasks=tasks):
            if event["type"] == "result":
                result = event["data"]
        return result

    async def execute_streaming(self, **kwargs) -> AsyncGenerator[dict, None]:
        """Create tasks one by one, yielding task_created events for live updates."""
        tasks: list[dict] = kwargs["tasks"]
        repo = TaskRepository(self.db)

        # Fetch existing task titles to prevent duplicates
        existing = await repo.list_by_project(self.project_id)
        existing_titles = {t.title.strip().lower() for t in existing}

        created_tasks = []
        skipped = []
        total = len(tasks)

        for i, t in enumerate(tasks):
            title = t["title"].strip()
            if title.lower() in existing_titles:
                skipped.append(title)
                continue

            parsed_due_date = None
            if t.get("due_date"):
                try:
                    parsed_due_date = date.fromisoformat(t["due_date"])
                except ValueError:
                    pass

            task_data = TaskCreate(
                title=title,
                description=t.get("description"),
                priority=t.get("priority", "medium"),
                assignee=t.get("assignee"),
                due_date=parsed_due_date,
            )

            task = await repo.create(self.project_id, task_data)
            created_tasks.append(task)

            # Emit progress event after each task
            yield {
                "type": "task_created",
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "priority": task.priority,
                    "status": task.status,
                },
                "progress": {"current": len(created_tasks), "total": total - len(skipped)},
            }

        if not created_tasks and skipped:
            yield {
                "type": "result",
                "data": {
                    "success": False,
                    "message": f"All {len(skipped)} task(s) already exist — nothing created.",
                    "skipped": skipped,
                    "count": 0,
                    "tasks": [],
                },
            }
            return

        msg = f"Created {len(created_tasks)} task(s) successfully."
        if skipped:
            msg += f" Skipped {len(skipped)} duplicate(s): {', '.join(skipped)}."

        yield {
            "type": "result",
            "data": {
                "success": True,
                "message": msg,
                "count": len(created_tasks),
                "tasks": [
                    {"id": str(t.id), "title": t.title, "priority": t.priority}
                    for t in created_tasks
                ],
                "skipped": skipped if skipped else None,
            },
        }


class UpdateTaskTool(BaseTool):
    """Tool for updating an existing task."""

    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id

    @property
    def name(self) -> str:
        return "update_task"

    @property
    def description(self) -> str:
        return """Update an existing task by its ID. Use list_tasks first to find the
        task ID, then call this with the ID and the fields to update.
        You can update any combination of: title, description, status, priority, assignee, due_date."""

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The UUID of the task to update",
                },
                "title": {
                    "type": "string",
                    "description": "New task title",
                },
                "description": {
                    "type": "string",
                    "description": "New task description",
                },
                "status": {
                    "type": "string",
                    "enum": ["todo", "in_progress", "review", "done"],
                    "description": "New task status",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "New task priority",
                },
                "assignee": {
                    "type": "string",
                    "description": "New assignee",
                },
                "due_date": {
                    "type": "string",
                    "description": "New due date in YYYY-MM-DD format",
                },
            },
            "required": ["task_id"],
        }

    async def execute(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> Any:
        repo = TaskRepository(self.db)

        # Verify the task belongs to this project
        task = await repo.get_by_id(UUID(task_id))
        if not task:
            return {"success": False, "error": f"Task not found: {task_id}"}
        if task.project_id != self.project_id:
            return {"success": False, "error": "Task does not belong to this project"}

        # Build update data
        update_fields: dict = {}
        if title is not None:
            update_fields["title"] = title
        if description is not None:
            update_fields["description"] = description
        if status is not None:
            update_fields["status"] = status
        if priority is not None:
            update_fields["priority"] = priority
        if assignee is not None:
            update_fields["assignee"] = assignee
        if due_date is not None:
            try:
                update_fields["due_date"] = date.fromisoformat(due_date)
            except ValueError:
                return {"success": False, "error": f"Invalid date format: {due_date}"}

        if not update_fields:
            return {"success": False, "error": "No fields to update"}

        update_data = TaskUpdate(**update_fields)
        updated_task = await repo.update(UUID(task_id), update_data)

        if not updated_task:
            return {"success": False, "error": "Failed to update task"}

        return {
            "success": True,
            "message": f"Task '{updated_task.title}' updated successfully.",
            "task": {
                "id": str(updated_task.id),
                "title": updated_task.title,
                "status": updated_task.status,
                "priority": updated_task.priority,
                "assignee": updated_task.assignee,
                "due_date": str(updated_task.due_date) if updated_task.due_date else None,
            },
        }


class DeleteTaskTool(BaseTool):
    """Tool for deleting a task."""

    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id

    @property
    def name(self) -> str:
        return "delete_task"

    @property
    def description(self) -> str:
        return """Delete a task by its ID. Use list_tasks first to find the task ID.
        This permanently removes the task from the project."""

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The UUID of the task to delete",
                },
            },
            "required": ["task_id"],
        }

    async def execute(self, task_id: str) -> Any:
        repo = TaskRepository(self.db)

        # Verify the task belongs to this project
        task = await repo.get_by_id(UUID(task_id))
        if not task:
            return {"success": False, "error": f"Task not found: {task_id}"}
        if task.project_id != self.project_id:
            return {"success": False, "error": "Task does not belong to this project"}

        task_title = task.title
        deleted = await repo.delete(UUID(task_id))

        if not deleted:
            return {"success": False, "error": "Failed to delete task"}

        return {
            "success": True,
            "message": f"Task '{task_title}' deleted successfully.",
        }
