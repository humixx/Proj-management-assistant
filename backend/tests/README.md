# Repository Tests

This directory contains comprehensive tests for all database repository classes.

## Running Tests

### Using the Test Runner

The easiest way to run tests is using the standalone test runner:

```bash
cd backend
python test_runner.py
```

### Environment Variables

The test runner uses the following environment variables for database connection:

- `POSTGRES_USER` - PostgreSQL username (default: "postgres")
- `POSTGRES_PASSWORD` - PostgreSQL password (default: "postgres")
- `POSTGRES_HOST` - PostgreSQL host (default: "localhost")
- `POSTGRES_PORT` - PostgreSQL port (default: "5432")

Example:
```bash
export POSTGRES_USER=myuser
export POSTGRES_PASSWORD=mypassword
python test_runner.py
```

### Using pytest

To run tests with pytest (requires pytest and pytest-asyncio):

```bash
pip install pytest pytest-asyncio aiosqlite
pytest tests/test_repositories/ -v
```

## Test Coverage

The test suite covers:

### ProjectRepository
- Create projects with and without settings
- Retrieve projects by ID
- List all projects with pagination
- Update projects (full and partial)
- Delete projects

### TaskRepository
- Create single and bulk tasks
- Retrieve tasks by ID
- List tasks with filtering (status, priority, assignee)
- Update tasks
- Delete tasks

### DocumentRepository
- Create document records
- Retrieve documents by ID
- List documents by project
- Add text chunks for RAG
- Mark documents as processed
- Delete documents with cascade

### ChatRepository
- Create chat messages
- Create messages with tool calls/results
- List messages by project
- Clear chat history
- Verify message isolation between projects

## Test Database

The test runner automatically creates a temporary test database (`project_assistant_test`) which is dropped and recreated on each run. This ensures tests run in a clean environment.
