"""Test Pydantic schemas for validation."""
import pytest
from datetime import datetime, date
from uuid import uuid4
from pydantic import ValidationError

from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectSettings,
)
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    BulkTaskCreate,
    BulkTaskResponse,
)
from app.schemas.document import (
    DocumentResponse,
    DocumentListResponse,
    SearchResult,
    SearchResponse,
)
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatMessageResponse,
    ChatHistoryResponse,
    ToolCallInfo,
    PlanInfo,
    PlanStep,
)
from app.schemas.integration import (
    SlackConnectRequest,
    SlackChannel,
    SlackChannelList,
    SlackIntegrationResponse,
    SlackMessageRequest,
    SlackMessageResponse,
)


class TestProjectSchemas:
    """Test project schemas."""
    
    def test_project_settings_defaults(self):
        """Test ProjectSettings with default values."""
        settings = ProjectSettings()
        assert settings.chunk_size == 512
        assert settings.chunk_overlap == 50
        assert settings.top_k == 5
        assert settings.similarity_threshold == 0.7
    
    def test_project_settings_custom(self):
        """Test ProjectSettings with custom values."""
        settings = ProjectSettings(
            chunk_size=1024,
            chunk_overlap=100,
            top_k=10,
            similarity_threshold=0.8
        )
        assert settings.chunk_size == 1024
        assert settings.chunk_overlap == 100
        assert settings.top_k == 10
        assert settings.similarity_threshold == 0.8
    
    def test_project_create_minimal(self):
        """Test ProjectCreate with minimal required fields."""
        project = ProjectCreate(name="Test Project")
        assert project.name == "Test Project"
        assert project.description is None
        assert project.settings is None
    
    def test_project_create_full(self):
        """Test ProjectCreate with all fields."""
        settings = ProjectSettings(chunk_size=1024)
        project = ProjectCreate(
            name="Test Project",
            description="A test project",
            settings=settings
        )
        assert project.name == "Test Project"
        assert project.description == "A test project"
        assert project.settings.chunk_size == 1024
    
    def test_project_create_validation_empty_name(self):
        """Test ProjectCreate fails with empty name."""
        with pytest.raises(ValidationError):
            ProjectCreate(name="")
    
    def test_project_update_partial(self):
        """Test ProjectUpdate with partial fields."""
        update = ProjectUpdate(name="Updated Name")
        assert update.name == "Updated Name"
        assert update.description is None
        assert update.settings is None
    
    def test_project_response_from_dict(self):
        """Test ProjectResponse creation from dict."""
        data = {
            "id": uuid4(),
            "name": "Test Project",
            "description": "Test description",
            "settings": {"chunk_size": 512},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        response = ProjectResponse(**data)
        assert response.name == "Test Project"
        assert response.description == "Test description"
    
    def test_project_list_response(self):
        """Test ProjectListResponse."""
        projects = [
            ProjectResponse(
                id=uuid4(),
                name=f"Project {i}",
                created_at=datetime.now()
            )
            for i in range(3)
        ]
        response = ProjectListResponse(projects=projects, total=3)
        assert len(response.projects) == 3
        assert response.total == 3


class TestTaskSchemas:
    """Test task schemas."""
    
    def test_task_create_minimal(self):
        """Test TaskCreate with minimal fields."""
        task = TaskCreate(title="Test Task")
        assert task.title == "Test Task"
        assert task.description is None
        assert task.priority == "medium"
        assert task.assignee is None
        assert task.due_date is None
        assert task.tags is None
        assert task.parent_task_id is None
    
    def test_task_create_full(self):
        """Test TaskCreate with all fields."""
        parent_id = uuid4()
        task = TaskCreate(
            title="Test Task",
            description="Task description",
            priority="high",
            assignee="john@example.com",
            due_date=date(2026, 2, 1),
            tags=["urgent", "backend"],
            parent_task_id=parent_id
        )
        assert task.title == "Test Task"
        assert task.priority == "high"
        assert task.assignee == "john@example.com"
        assert task.due_date == date(2026, 2, 1)
        assert len(task.tags) == 2
        assert task.parent_task_id == parent_id
    
    def test_task_create_validation(self):
        """Test TaskCreate validation."""
        with pytest.raises(ValidationError):
            TaskCreate(title="")  # Empty title
    
    def test_task_update_partial(self):
        """Test TaskUpdate with partial fields."""
        update = TaskUpdate(status="completed", priority="low")
        assert update.status == "completed"
        assert update.priority == "low"
        assert update.title is None
    
    def test_task_response_from_dict(self):
        """Test TaskResponse creation."""
        data = {
            "id": uuid4(),
            "project_id": uuid4(),
            "title": "Test Task",
            "status": "pending",
            "priority": "medium",
            "created_at": datetime.now(),
        }
        response = TaskResponse(**data)
        assert response.title == "Test Task"
        assert response.status == "pending"
    
    def test_bulk_task_create(self):
        """Test BulkTaskCreate."""
        tasks = [
            TaskCreate(title=f"Task {i}")
            for i in range(3)
        ]
        bulk = BulkTaskCreate(tasks=tasks)
        assert len(bulk.tasks) == 3
    
    def test_bulk_task_response(self):
        """Test BulkTaskResponse."""
        created = [
            TaskResponse(
                id=uuid4(),
                project_id=uuid4(),
                title=f"Task {i}",
                status="pending",
                priority="medium",
                created_at=datetime.now()
            )
            for i in range(3)
        ]
        response = BulkTaskResponse(created=created, count=3)
        assert response.count == 3
        assert len(response.created) == 3


class TestDocumentSchemas:
    """Test document schemas."""
    
    def test_document_response(self):
        """Test DocumentResponse."""
        doc = DocumentResponse(
            id=uuid4(),
            project_id=uuid4(),
            filename="test.pdf",
            file_type="application/pdf",
            file_size=1024,
            processed=True,
            chunk_count=10,
            created_at=datetime.now()
        )
        assert doc.filename == "test.pdf"
        assert doc.file_type == "application/pdf"
        assert doc.processed is True
        assert doc.chunk_count == 10
    
    def test_document_list_response(self):
        """Test DocumentListResponse."""
        docs = [
            DocumentResponse(
                id=uuid4(),
                project_id=uuid4(),
                filename=f"doc{i}.pdf",
                processed=True,
                chunk_count=5,
                created_at=datetime.now()
            )
            for i in range(3)
        ]
        response = DocumentListResponse(documents=docs, total=3)
        assert len(response.documents) == 3
        assert response.total == 3
    
    def test_search_result(self):
        """Test SearchResult."""
        result = SearchResult(
            chunk_text="This is a test chunk",
            document_id=uuid4(),
            document_name="test.pdf",
            page_number=1,
            score=0.95
        )
        assert result.chunk_text == "This is a test chunk"
        assert result.score == 0.95
        assert result.page_number == 1
    
    def test_search_response(self):
        """Test SearchResponse."""
        results = [
            SearchResult(
                chunk_text=f"Chunk {i}",
                document_id=uuid4(),
                document_name="test.pdf",
                score=0.9 - (i * 0.1)
            )
            for i in range(3)
        ]
        response = SearchResponse(
            results=results,
            query="test query",
            total=3
        )
        assert len(response.results) == 3
        assert response.query == "test query"
        assert response.total == 3


class TestChatSchemas:
    """Test chat schemas."""
    
    def test_chat_request_minimal(self):
        """Test ChatRequest with minimal fields."""
        request = ChatRequest(message="Hello")
        assert request.message == "Hello"
        assert request.include_context is True
    
    def test_chat_request_no_context(self):
        """Test ChatRequest without context."""
        request = ChatRequest(message="Hello", include_context=False)
        assert request.message == "Hello"
        assert request.include_context is False
    
    def test_chat_request_validation(self):
        """Test ChatRequest validation."""
        with pytest.raises(ValidationError):
            ChatRequest(message="")  # Empty message
    
    def test_tool_call_info(self):
        """Test ToolCallInfo."""
        tool_call = ToolCallInfo(
            tool_name="create_task",
            arguments={"title": "New Task", "priority": "high"},
            result={"task_id": str(uuid4())}
        )
        assert tool_call.tool_name == "create_task"
        assert tool_call.arguments["title"] == "New Task"
        assert "task_id" in tool_call.result
    
    def test_plan_step(self):
        """Test PlanStep."""
        step = PlanStep(
            step_id=1,
            action="create_task",
            description="Create a new task",
            status="completed"
        )
        assert step.step_id == 1
        assert step.action == "create_task"
        assert step.status == "completed"
    
    def test_plan_info(self):
        """Test PlanInfo."""
        steps = [
            PlanStep(
                step_id=i,
                action=f"action_{i}",
                description=f"Step {i}",
                status="pending"
            )
            for i in range(3)
        ]
        plan = PlanInfo(
            plan_id="plan-123",
            goal="Complete the project",
            steps=steps,
            current_step=0,
            status="in_progress"
        )
        assert plan.plan_id == "plan-123"
        assert len(plan.steps) == 3
        assert plan.current_step == 0
    
    def test_chat_response_simple(self):
        """Test ChatResponse without tool calls."""
        response = ChatResponse(message="Hello, how can I help?")
        assert response.message == "Hello, how can I help?"
        assert response.tool_calls is None
        assert response.plan is None
    
    def test_chat_response_with_tool_calls(self):
        """Test ChatResponse with tool calls."""
        tool_calls = [
            ToolCallInfo(
                tool_name="create_task",
                arguments={"title": "Task 1"},
                result={"success": True}
            )
        ]
        response = ChatResponse(
            message="Created a task",
            tool_calls=tool_calls
        )
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].tool_name == "create_task"
    
    def test_chat_message_response(self):
        """Test ChatMessageResponse."""
        message = ChatMessageResponse(
            id=uuid4(),
            role="user",
            content="Hello",
            created_at=datetime.now()
        )
        assert message.role == "user"
        assert message.content == "Hello"
    
    def test_chat_history_response(self):
        """Test ChatHistoryResponse."""
        messages = [
            ChatMessageResponse(
                id=uuid4(),
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                created_at=datetime.now()
            )
            for i in range(4)
        ]
        history = ChatHistoryResponse(messages=messages, total=4)
        assert len(history.messages) == 4
        assert history.total == 4


class TestIntegrationSchemas:
    """Test integration schemas."""
    
    def test_slack_connect_request(self):
        """Test SlackConnectRequest."""
        request = SlackConnectRequest(
            code="auth-code-123",
            redirect_uri="https://example.com/callback"
        )
        assert request.code == "auth-code-123"
        assert request.redirect_uri == "https://example.com/callback"
    
    def test_slack_connect_validation(self):
        """Test SlackConnectRequest validation."""
        with pytest.raises(ValidationError):
            SlackConnectRequest(code="", redirect_uri="")
    
    def test_slack_channel(self):
        """Test SlackChannel."""
        channel = SlackChannel(id="C123456", name="general")
        assert channel.id == "C123456"
        assert channel.name == "general"
    
    def test_slack_channel_list(self):
        """Test SlackChannelList."""
        channels = [
            SlackChannel(id=f"C{i}", name=f"channel-{i}")
            for i in range(3)
        ]
        channel_list = SlackChannelList(channels=channels)
        assert len(channel_list.channels) == 3
    
    def test_slack_integration_response(self):
        """Test SlackIntegrationResponse."""
        integration = SlackIntegrationResponse(
            id=uuid4(),
            team_name="My Team",
            channel_name="general",
            connected=True,
            created_at=datetime.now()
        )
        assert integration.team_name == "My Team"
        assert integration.channel_name == "general"
        assert integration.connected is True
    
    def test_slack_message_request(self):
        """Test SlackMessageRequest."""
        request = SlackMessageRequest(
            channel="C123456",
            message="Hello from the app!"
        )
        assert request.channel == "C123456"
        assert request.message == "Hello from the app!"
    
    def test_slack_message_request_validation(self):
        """Test SlackMessageRequest validation."""
        with pytest.raises(ValidationError):
            SlackMessageRequest(channel="", message="")
    
    def test_slack_message_response_success(self):
        """Test SlackMessageResponse for successful send."""
        response = SlackMessageResponse(
            success=True,
            ts="1234567890.123456",
            channel="C123456"
        )
        assert response.success is True
        assert response.ts == "1234567890.123456"
        assert response.channel == "C123456"
    
    def test_slack_message_response_failure(self):
        """Test SlackMessageResponse for failed send."""
        response = SlackMessageResponse(
            success=False,
            ts=None,
            channel="C123456"
        )
        assert response.success is False
        assert response.ts is None


class TestSchemaIntegration:
    """Test schema integration scenarios."""
    
    def test_nested_project_settings(self):
        """Test nested ProjectSettings in ProjectCreate."""
        settings = ProjectSettings(chunk_size=2048, top_k=20)
        project = ProjectCreate(
            name="RAG Project",
            description="Project with custom RAG settings",
            settings=settings
        )
        assert project.settings.chunk_size == 2048
        assert project.settings.top_k == 20
        assert project.settings.chunk_overlap == 50  # Default
    
    def test_task_with_subtasks(self):
        """Test task hierarchy with parent_task_id."""
        parent_task = TaskCreate(title="Parent Task")
        subtask = TaskCreate(
            title="Subtask",
            parent_task_id=uuid4()
        )
        assert subtask.parent_task_id is not None
    
    def test_bulk_operations(self):
        """Test bulk task operations."""
        tasks = [
            TaskCreate(title=f"Task {i}", priority="high")
            for i in range(5)
        ]
        bulk_create = BulkTaskCreate(tasks=tasks)
        assert len(bulk_create.tasks) == 5
        assert all(t.priority == "high" for t in bulk_create.tasks)
    
    def test_search_workflow(self):
        """Test search result workflow."""
        # Create search results
        results = [
            SearchResult(
                chunk_text=f"Result {i}",
                document_id=uuid4(),
                document_name=f"doc{i}.pdf",
                page_number=i + 1,
                score=0.95 - (i * 0.05)
            )
            for i in range(5)
        ]
        
        # Create search response
        response = SearchResponse(
            results=results,
            query="test query",
            total=5
        )
        
        # Verify sorting by score
        assert response.results[0].score > response.results[1].score
        assert len(response.results) == 5
    
    def test_chat_with_plan_and_tools(self):
        """Test complete chat workflow with plan and tool calls."""
        # Create plan steps
        steps = [
            PlanStep(
                step_id=i,
                action=f"step_{i}",
                description=f"Execute step {i}",
                status="completed" if i < 2 else "pending"
            )
            for i in range(3)
        ]
        
        # Create plan
        plan = PlanInfo(
            plan_id="plan-abc",
            goal="Complete user request",
            steps=steps,
            current_step=2,
            status="in_progress"
        )
        
        # Create tool calls
        tool_calls = [
            ToolCallInfo(
                tool_name="create_task",
                arguments={"title": "New Task"},
                result={"task_id": str(uuid4())}
            ),
            ToolCallInfo(
                tool_name="search_documents",
                arguments={"query": "test"},
                result={"count": 5}
            )
        ]
        
        # Create complete response
        response = ChatResponse(
            message="I've executed your request",
            tool_calls=tool_calls,
            plan=plan
        )
        
        assert len(response.tool_calls) == 2
        assert response.plan.current_step == 2
        assert response.plan.steps[0].status == "completed"
