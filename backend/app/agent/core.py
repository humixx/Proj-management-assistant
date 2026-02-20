"""Main agent implementation."""
import json
from typing import Any, AsyncGenerator, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.memory import AgentMemory
from app.agent.prompts import get_system_prompt
from app.agent.tools import (
    ToolRegistry,
    SearchDocumentsTool,
    ListTasksTool,
    ProposeTasksTool,
    ConfirmProposedTasksTool,
    UpdateTaskTool,
    DeleteTaskTool,
    ProposePlanTool,
    ConfirmPlanTool,
)
from app.services.llm_service import get_llm_provider


class Agent:
    """Main agent that orchestrates conversations and tool usage."""

    def __init__(self, db: AsyncSession, project_id: UUID, llm_config: Optional[dict] = None):
        """
        Initialize the agent.

        Args:
            db: Database session
            project_id: Current project ID
            llm_config: Optional dict with 'llm_provider' and 'llm_model' keys.
                        Defaults to Anthropic Claude if not provided.
        """
        self.db = db
        self.project_id = project_id
        self.memory = AgentMemory(db, project_id)
        self.system_prompt = get_system_prompt(str(project_id))
        config = llm_config or {}
        self.llm = get_llm_provider(
            provider=config.get("llm_provider", "anthropic"),
            model=config.get("llm_model"),
        )

        # Initialize tool registry
        self.tools = ToolRegistry()
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all available tools."""
        self.tools.register(SearchDocumentsTool(self.db, self.project_id))
        self.tools.register(ListTasksTool(self.db, self.project_id))
        self.tools.register(ProposeTasksTool(self.db, self.project_id))
        self.tools.register(ConfirmProposedTasksTool(self.db, self.project_id))
        self.tools.register(UpdateTaskTool(self.db, self.project_id))
        self.tools.register(DeleteTaskTool(self.db, self.project_id))
        self.tools.register(ProposePlanTool(self.db, self.project_id))
        self.tools.register(ConfirmPlanTool(self.db, self.project_id))

    async def run(self, user_message: str) -> dict:
        """
        Process a user message and return the agent's response.

        Args:
            user_message: The user's input message

        Returns:
            Dict with message, tool_calls, and any other response data
        """
        # Save user message
        await self.memory.save_message(role="user", content=user_message)

        # Get chat history for context
        history = await self.memory.get_chat_history(limit=10)

        # Build messages for LLM
        messages = history.copy()
        if not messages or messages[-1]["content"] != user_message:
            messages.append({"role": "user", "content": user_message})

        # Get tool definitions
        tool_definitions = self.tools.get_tool_definitions()

        # Track tool calls for response
        all_tool_calls = []

        # Agent loop - keep processing until we get a final response
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Call LLM
            response = await self.llm.chat(
                messages=messages,
                system_prompt=self.system_prompt,
                tools=tool_definitions,
            )

            # If no tool calls, we have our final response
            if not response["tool_calls"]:
                final_message = response["content"]

                # Save assistant response
                await self.memory.save_message(
                    role="assistant",
                    content=final_message,
                    tool_calls={"calls": all_tool_calls} if all_tool_calls else None,
                )

                return {
                    "message": final_message,
                    "tool_calls": all_tool_calls if all_tool_calls else None,
                }

            # Process tool calls
            tool_results = []
            for tool_call in response["tool_calls"]:
                tool_name = tool_call["name"]
                tool_args = tool_call["arguments"]

                # Get and execute tool
                tool = self.tools.get(tool_name)
                if tool:
                    try:
                        result = await tool.execute(**tool_args)
                    except Exception as e:
                        result = {"error": str(e)}
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}

                tool_results.append({
                    "tool_use_id": tool_call["id"],
                    "result": result,
                })

                # Track for response
                all_tool_calls.append({
                    "tool_name": tool_name,
                    "arguments": tool_args,
                    "result": result,
                })

            # Add assistant message with tool use to history
            assistant_content = []
            if response["content"]:
                assistant_content.append({"type": "text", "text": response["content"]})
            for tc in response["tool_calls"]:
                assistant_content.append({
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["name"],
                    "input": tc["arguments"],
                })

            messages.append({"role": "assistant", "content": assistant_content})

            # Add tool results
            tool_result_content = []
            for tr in tool_results:
                tool_result_content.append({
                    "type": "tool_result",
                    "tool_use_id": tr["tool_use_id"],
                    "content": json.dumps(tr["result"]),
                })

            messages.append({"role": "user", "content": tool_result_content})

        # Max iterations reached
        return {
            "message": "I apologize, but I wasn't able to complete the request. Please try again.",
            "tool_calls": all_tool_calls if all_tool_calls else None,
        }

    async def run_streaming(self, user_message: str) -> AsyncGenerator[dict, None]:
        """
        Process a user message and yield progress events as they happen.

        Yields dicts like:
          {"type": "thinking", "stage": "calling_llm"}
          {"type": "tool_start", "tool_name": "create_task", "arguments": {...}}
          {"type": "tool_end", "tool_name": "create_task", "result": {...}}
          {"type": "response", "message": "...", "tool_calls": [...]}
        """
        # Save user message
        await self.memory.save_message(role="user", content=user_message)

        # Get chat history for context
        history = await self.memory.get_chat_history(limit=10)

        # Build messages for LLM
        messages = history.copy()
        if not messages or messages[-1]["content"] != user_message:
            messages.append({"role": "user", "content": user_message})

        # Get tool definitions
        tool_definitions = self.tools.get_tool_definitions()

        # Track tool calls for response
        all_tool_calls = []

        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Tell the frontend we're calling the LLM — include context
            # about what happened so far so labels can be more specific.
            yield {
                "type": "thinking",
                "stage": "calling_llm",
                "iteration": iteration,
                "has_tool_calls": len(all_tool_calls) > 0,
                "last_tool": all_tool_calls[-1]["tool_name"] if all_tool_calls else None,
            }

            # Call LLM with streaming — forward text deltas to the frontend
            response = None
            async for llm_event in self.llm.chat_streaming(
                messages=messages,
                system_prompt=self.system_prompt,
                tools=tool_definitions,
            ):
                if llm_event["type"] == "text_delta":
                    yield {"type": "text_delta", "text": llm_event["text"]}
                elif llm_event["type"] == "result":
                    response = llm_event

            if response is None:
                response = {"content": "", "tool_calls": [], "stop_reason": "error"}

            # If no tool calls, we have our final response
            if not response["tool_calls"]:
                final_message = response["content"]

                await self.memory.save_message(
                    role="assistant",
                    content=final_message,
                    tool_calls={"calls": all_tool_calls} if all_tool_calls else None,
                )

                yield {
                    "type": "response",
                    "message": final_message,
                    "tool_calls": all_tool_calls if all_tool_calls else None,
                }
                return

            # Process tool calls
            tool_results = []
            for tool_call in response["tool_calls"]:
                tool_name = tool_call["name"]
                tool_args = tool_call["arguments"]

                # Emit tool_start
                yield {
                    "type": "tool_start",
                    "tool_name": tool_name,
                    "arguments": tool_args,
                }

                # Execute tool — use streaming path when available
                tool = self.tools.get(tool_name)
                result = None
                if tool:
                    try:
                        if tool.supports_streaming:
                            async for event in tool.execute_streaming(**tool_args):
                                if event["type"] == "result":
                                    result = event["data"]
                                else:
                                    # Forward intermediate events (e.g. task_created)
                                    yield {**event, "tool_name": tool_name}
                        else:
                            result = await tool.execute(**tool_args)
                    except Exception as e:
                        result = {"error": str(e)}
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}

                # Emit tool_end
                yield {
                    "type": "tool_end",
                    "tool_name": tool_name,
                    "result": result,
                }

                tool_results.append({
                    "tool_use_id": tool_call["id"],
                    "result": result,
                })

                all_tool_calls.append({
                    "tool_name": tool_name,
                    "arguments": tool_args,
                    "result": result,
                })

            # Add assistant message with tool use to history
            assistant_content = []
            if response["content"]:
                assistant_content.append({"type": "text", "text": response["content"]})
            for tc in response["tool_calls"]:
                assistant_content.append({
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["name"],
                    "input": tc["arguments"],
                })

            messages.append({"role": "assistant", "content": assistant_content})

            tool_result_content = []
            for tr in tool_results:
                tool_result_content.append({
                    "type": "tool_result",
                    "tool_use_id": tr["tool_use_id"],
                    "content": json.dumps(tr["result"]),
                })

            messages.append({"role": "user", "content": tool_result_content})

        # Max iterations reached
        yield {
            "type": "response",
            "message": "I apologize, but I wasn't able to complete the request. Please try again.",
            "tool_calls": all_tool_calls if all_tool_calls else None,
        }
