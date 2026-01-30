"""Test script for verifying implemented components."""
import asyncio
import sys
from uuid import uuid4

# Test imports
print("=" * 60)
print("Testing imports...")
print("=" * 60)

try:
    from app.services.llm_service import llm_service, LLMService
    print("✓ LLM Service imported successfully")
except Exception as e:
    print(f"✗ Failed to import LLM Service: {e}")
    sys.exit(1)

try:
    from app.agent.tools.base import BaseTool
    from app.agent.tools.registry import ToolRegistry
    print("✓ Base tool and registry imported successfully")
except Exception as e:
    print(f"✗ Failed to import tools base: {e}")
    sys.exit(1)

try:
    from app.agent.tools.rag_tools import SearchDocumentsTool
    print("✓ RAG tools imported successfully")
except Exception as e:
    print(f"✗ Failed to import RAG tools: {e}")
    sys.exit(1)

try:
    from app.agent.tools.task_tools import CreateTaskTool, BulkCreateTasksTool, ListTasksTool
    print("✓ Task tools imported successfully")
except Exception as e:
    print(f"✗ Failed to import task tools: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Testing LLM Service initialization...")
print("=" * 60)

try:
    service = LLMService()
    print(f"✓ LLM Service initialized")
    print(f"  - Model: {service.model}")
    print(f"  - Client type: {type(service.client).__name__}")
except Exception as e:
    print(f"✗ Failed to initialize LLM Service: {e}")

print("\n" + "=" * 60)
print("Testing Tool Registry...")
print("=" * 60)

try:
    registry = ToolRegistry()
    print("✓ Tool Registry initialized")
    print(f"  - Initial tools: {len(registry.get_all())}")
except Exception as e:
    print(f"✗ Failed to initialize registry: {e}")

print("\n" + "=" * 60)
print("Testing tool definitions (Claude format)...")
print("=" * 60)

# Mock database session for testing tool initialization
class MockDB:
    """Mock database session for testing."""
    pass

try:
    mock_db = MockDB()
    project_id = uuid4()
    
    # Test SearchDocumentsTool
    search_tool = SearchDocumentsTool(mock_db, project_id)
    search_def = search_tool.to_claude_format()
    print(f"\n✓ SearchDocumentsTool definition:")
    print(f"  - Name: {search_def['name']}")
    print(f"  - Description: {search_def['description'][:60]}...")
    print(f"  - Required params: {search_def['input_schema']['required']}")
    
    # Test CreateTaskTool
    create_tool = CreateTaskTool(mock_db, project_id)
    create_def = create_tool.to_claude_format()
    print(f"\n✓ CreateTaskTool definition:")
    print(f"  - Name: {create_def['name']}")
    print(f"  - Description: {create_def['description'][:60]}...")
    print(f"  - Required params: {create_def['input_schema']['required']}")
    
    # Test BulkCreateTasksTool
    bulk_tool = BulkCreateTasksTool(mock_db, project_id)
    bulk_def = bulk_tool.to_claude_format()
    print(f"\n✓ BulkCreateTasksTool definition:")
    print(f"  - Name: {bulk_def['name']}")
    print(f"  - Description: {bulk_def['description'][:60]}...")
    print(f"  - Required params: {bulk_def['input_schema']['required']}")
    
    # Test ListTasksTool
    list_tool = ListTasksTool(mock_db, project_id)
    list_def = list_tool.to_claude_format()
    print(f"\n✓ ListTasksTool definition:")
    print(f"  - Name: {list_def['name']}")
    print(f"  - Description: {list_def['description'][:60]}...")
    print(f"  - Has parameters: {len(list_def['input_schema']['properties']) > 0}")
    
except Exception as e:
    print(f"✗ Failed to test tools: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Testing Tool Registry with tools...")
print("=" * 60)

try:
    registry = ToolRegistry()
    
    # Register tools
    registry.register(search_tool)
    registry.register(create_tool)
    registry.register(bulk_tool)
    registry.register(list_tool)
    
    print(f"✓ Registered {len(registry.get_all())} tools")
    print(f"  - Tool names: {registry.list_names()}")
    
    # Get tool definitions for Claude
    tool_defs = registry.get_tool_definitions()
    print(f"\n✓ Generated {len(tool_defs)} tool definitions for Claude API")
    
    # Verify we can get individual tools
    retrieved_tool = registry.get("search_documents")
    print(f"\n✓ Successfully retrieved tool: {retrieved_tool.name}")
    
except Exception as e:
    print(f"✗ Failed to test registry: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED!")
print("=" * 60)
