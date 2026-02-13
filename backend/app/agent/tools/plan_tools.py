"""Plan management tools for the agent."""
from typing import Any, AsyncGenerator, Optional
from uuid import UUID
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.base import BaseTool
from app.db.repositories import TaskRepository, PlanRepository
from app.schemas import TaskCreate


class ProposePlanTool(BaseTool):
    """Tool for proposing a multi-step plan. Does NOT create anything in the database."""

    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id

    @property
    def name(self) -> str:
        return "propose_plan"

    @property
    def description(self) -> str:
        return """Propose a multi-step plan for a complex goal. Breaks the goal into
        an ordered sequence of steps. The plan is NOT created until the user approves it.
        After approval, call confirm_plan to create the tasks.

        AUTOMATICALLY use this (without being asked) when the request involves:
        - A high-level goal with 3+ sequential steps (e.g., "build auth", "set up CI/CD")
        - Steps that depend on each other (design DB → build API → create UI)
        - Work spanning multiple layers (database, backend, frontend, testing)
        - Ambitious goals using words like "build", "implement", "set up", "launch"

        Use propose_tasks INSTEAD only for simple unordered, independent task lists."""

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "goal": {
                    "type": "string",
                    "description": "The high-level goal to decompose into steps",
                },
                "steps": {
                    "type": "array",
                    "description": "Ordered list of steps to achieve the goal",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Clear, actionable step title",
                            },
                            "description": {
                                "type": "string",
                                "description": "What needs to be done in this step",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                                "description": "Step priority (default: medium)",
                            },
                            "assignee": {
                                "type": "string",
                                "description": "Person assigned to this step",
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
            "required": ["goal", "steps"],
        }

    async def execute(self, goal: str, steps: list[dict]) -> Any:
        proposed_steps = []
        for i, step in enumerate(steps):
            proposed_steps.append({
                "step_number": i + 1,
                "title": step["title"],
                "description": step.get("description"),
                "priority": step.get("priority", "medium"),
                "assignee": step.get("assignee"),
                "due_date": step.get("due_date"),
            })

        return {
            "type": "plan_proposal",
            "message": (
                f"Proposed a {len(proposed_steps)}-step plan for: {goal}. "
                f"Review and approve to create these as tasks."
            ),
            "goal": goal,
            "steps": proposed_steps,
        }


class ConfirmPlanTool(BaseTool):
    """Tool for creating tasks from an approved plan."""

    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id

    @property
    def name(self) -> str:
        return "confirm_plan"

    @property
    def description(self) -> str:
        return """Create tasks from an approved plan. Only call this AFTER the user
        has explicitly approved the proposed plan. Creates a parent task for the goal
        and subtasks for each step, linked via parent_task_id with proper ordering."""

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "goal": {
                    "type": "string",
                    "description": "The high-level goal (becomes the parent task title)",
                },
                "steps": {
                    "type": "array",
                    "description": "Ordered list of steps to create as subtasks",
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
            "required": ["goal", "steps"],
        }

    @property
    def supports_streaming(self) -> bool:
        return True

    async def execute(self, goal: str, steps: list[dict]) -> Any:
        """Non-streaming fallback — creates all at once."""
        result: Any = None
        async for event in self.execute_streaming(goal=goal, steps=steps):
            if event["type"] == "result":
                result = event["data"]
        return result

    async def execute_streaming(self, **kwargs) -> AsyncGenerator[dict, None]:
        """Create parent task + subtasks one by one, yielding progress events."""
        goal: str = kwargs["goal"]
        steps: list[dict] = kwargs["steps"]
        task_repo = TaskRepository(self.db)

        # 1. Create the parent task (the goal itself)
        parent_data = TaskCreate(
            title=goal,
            description=f"Plan: {goal}",
            priority="high",
        )
        parent_task = await task_repo.create(self.project_id, parent_data)

        yield {
            "type": "plan_started",
            "plan_goal": goal,
            "parent_task_id": str(parent_task.id),
            "total_steps": len(steps),
        }

        # 2. Check existing subtasks to prevent duplicates
        existing_subtasks = await task_repo.list_subtasks(parent_task.id)
        existing_titles = {t.title.strip().lower() for t in existing_subtasks}

        # 3. Create each step as a subtask with order
        step_task_ids = []
        skipped = []

        for i, step in enumerate(steps):
            title = step["title"].strip()
            if title.lower() in existing_titles:
                skipped.append(title)
                continue

            parsed_due_date = None
            if step.get("due_date"):
                try:
                    parsed_due_date = date.fromisoformat(step["due_date"])
                except ValueError:
                    pass

            task_data = TaskCreate(
                title=title,
                description=step.get("description"),
                priority=step.get("priority", "medium"),
                assignee=step.get("assignee"),
                due_date=parsed_due_date,
                parent_task_id=parent_task.id,
            )
            task = await task_repo.create(self.project_id, task_data)

            # Set order on the task
            task.order = i
            await self.db.commit()
            await self.db.refresh(task)

            step_task_ids.append(task.id)

            yield {
                "type": "plan_step_created",
                "step_number": i + 1,
                "total_steps": len(steps),
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "priority": task.priority,
                    "status": task.status,
                },
            }

        # 4. Create the plan metadata row
        plan_repo = PlanRepository(self.db)
        plan = await plan_repo.create(
            project_id=self.project_id,
            goal=goal,
            parent_task_id=parent_task.id,
            step_order=[str(tid) for tid in step_task_ids],
        )

        msg = f"Created plan '{goal}' with {len(step_task_ids)} step(s)."
        if skipped:
            msg += f" Skipped {len(skipped)} duplicate(s): {', '.join(skipped)}."

        yield {
            "type": "result",
            "data": {
                "success": True,
                "message": msg,
                "plan_id": str(plan.id),
                "parent_task_id": str(parent_task.id),
                "steps": [
                    {"task_id": str(tid), "title": steps[i]["title"], "step_number": i + 1}
                    for i, tid in enumerate(step_task_ids)
                ],
            },
        }
