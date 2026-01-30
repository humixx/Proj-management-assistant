"""Task management tools for the agent."""
from typing import Any, Optional
from uuid import UUID
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.base import BaseTool
from app.db.repositories import TaskRepository
from app.schemas import TaskCreate


class CreateTaskTool(BaseTool):
    """Tool for creating a single task."""
    
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
    """Tool for creating multiple tasks at once."""
    
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
        Use to see current tasks, their status, and priorities."""
    
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
