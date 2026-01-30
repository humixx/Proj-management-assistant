"""Main agent implementation."""
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.memory import AgentMemory
from app.agent.prompts import get_system_prompt
from app.agent.tools import (
    ToolRegistry,
    SearchDocumentsTool,
    CreateTaskTool,
    BulkCreateTasksTool,
    ListTasksTool,
)
from app.services.llm_service import llm_service


class Agent:
    """Main agent that orchestrates conversations and tool usage."""
    
    def __init__(self, db: AsyncSession, project_id: UUID):
        """
        Initialize the agent.
        
        Args:
            db: Database session
            project_id: Current project ID
        """
        self.db = db
        self.project_id = project_id
        self.memory = AgentMemory(db, project_id)
        self.system_prompt = get_system_prompt(str(project_id))
        
        # Initialize tool registry
        self.tools = ToolRegistry()
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register all available tools."""
        self.tools.register(SearchDocumentsTool(self.db, self.project_id))
        self.tools.register(CreateTaskTool(self.db, self.project_id))
        self.tools.register(BulkCreateTasksTool(self.db, self.project_id))
        self.tools.register(ListTasksTool(self.db, self.project_id))
    
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
            response = await llm_service.chat(
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
                import json
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
