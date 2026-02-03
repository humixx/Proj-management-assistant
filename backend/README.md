# Backend - Project Management Assistant

FastAPI-based backend with AI agent, task management, document processing, and vector search capabilities.

## Features

- **AI Chat Agent**: Claude-powered assistant with tool execution
- **Task Management**: Create, update, and track tasks with subtasks
- **Document Processing**: Upload and process documents with vector embeddings
- **RAG (Retrieval Augmented Generation)**: Context-aware responses using document chunks
- **Slack Integration**: Connect projects to Slack channels
- **Vector Search**: pgvector-powered semantic search

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with pgvector extension
- **ORM**: SQLAlchemy (async)
- **Migrations**: Alembic
- **Vector Embeddings**: Voyage AI
- **AI**: Anthropic Claude
- **Caching**: Redis

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ with pgvector extension
- Redis server

### Installation

1. **Create virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Setup database**:
   ```bash
   # Create database
   createdb project_assistant
   
   # Run migrations
   alembic upgrade head
   
   # Or use the helper script
   python reset_db.py
   ```

5. **Run the server**:
   ```bash
   # Recommended: Use the startup script (checks database first)
   python start.py
   
   # Or directly with uvicorn
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/project_assistant

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys
VOYAGE_API_KEY=your_voyage_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Slack (Optional)
SLACK_CLIENT_ID=your_slack_client_id
SLACK_CLIENT_SECRET=your_slack_client_secret

# File Upload
UPLOAD_DIR=./uploads

# RAG Configuration
CHUNK_SIZE=512
CHUNK_OVERLAP=50
EMBEDDING_DIMENSION=1024
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.3
```

## Database Migrations

### Common Commands

```bash
# Check current migration version
alembic current

# Create new migration after model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Troubleshooting

If you encounter issues with database migrations or missing data:

```bash
# Check for migration issues
python alembic/scripts/check_migrations

# Reset database to clean state
python alembic/scripts/reset_db

# Verify database health
python alembic/scripts/verify_db
```

For detailed migration guide, see [alembic/MIGRATIONS.md](alembic/MIGRATIONS.md)

## API Documentation

Once the server is running, visit:

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── alembic/                 # Database migrations
│   ├── versions/           # Migration files
│   ├── scripts/            # Database management scripts
│   ├── env.py             # Alembic configuration
│   └── MIGRATIONS.md      # Migration guide
├── app/
│   ├── api/               # API routes
│   │   └── routes/       # Route modules
│   ├── db/               # Database
│   │   ├── models.py    # SQLAlchemy models
│   │   └── database.py  # Database connection
│   ├── services/         # Business logic
│   │   ├── ai_agent.py  # AI agent orchestration
│   │   ├── embeddings.py # Vector embeddings
│   │   └── rag.py       # RAG implementation
│   ├── schemas/          # Pydantic models
│   ├── config.py         # Configuration
│   └── main.py           # FastAPI application
├── uploads/              # Uploaded files storage
├── alembic.ini          # Alembic configuration
├── requirements.txt     # Python dependencies
├── reset_db.py         # Database reset helper
├── check_migrations.py # Migration checker
└── README.md           # This file
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

### Adding New Features

1. **Create models** in `app/db/models.py`
2. **Generate migration**: `alembic revision --autogenerate -m "description"`
3. **Check migration**: `python check_migrations.py`
4. **Apply migration**: `alembic upgrade head`
5. **Create schemas** in `app/schemas/`
6. **Add routes** in `app/api/routes/`
7. **Implement services** in `app/services/`

## Common Issues

### Issue: Database tables are empty

**Solution**: Run `python reset_db.py`

### Issue: Migration errors

**Solution**: 
1. Run `python check_migrations.py` to identify issues
2. Delete any empty migration files in `alembic/versions/`
3. Run `alembic upgrade head`

### Issue: pgvector extension not found

**Solution**: 
```sql
-- Connect to your database and run:
CREATE EXTENSION vector;
```

### Issue: Redis connection failed

**Solution**: Make sure Redis is running:
```bash
# Windows (if installed via installer)
redis-server

# Linux
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:latest
```

## API Endpoints

### Projects
- `GET /projects` - List all projects
- `POST /projects` - Create new project
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

### Tasks
- `GET /projects/{id}/tasks` - List project tasks
- `POST /tasks` - Create new task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

### Chat
- `POST /chat` - Send chat message
- `GET /chat/history` - Get chat history

### Documents
- `POST /documents/upload` - Upload document
- `GET /documents/{project_id}` - List project documents
- `DELETE /documents/{id}` - Delete document

### Slack
- `GET /slack/auth` - Start Slack OAuth flow
- `GET /slack/callback` - OAuth callback
- `GET /slack/integration/{project_id}` - Get integration status

## License

MIT

