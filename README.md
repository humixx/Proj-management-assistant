# Project Management Assistant

A comprehensive project management assistant with AI-powered chat, task management, document processing, and Slack integration (coming soon).

## 🚀 Quick Start

**New to this project?** Follow our [Quick Start Guide](QUICK_START.md) to get running in 5 minutes.

**Having issues?** Check the [Troubleshooting Guide](TROUBLESHOOTING.md).

## Project Structure

This project follows a monorepo structure with separate backend and frontend applications.

### Backend
- FastAPI-based REST API
- PostgreSQL with pgvector for vector storage
- AI agent with tool-based execution
- Document processing and RAG capabilities
- Slack integration

### Frontend
- Next.js with TypeScript
- React components
- Real-time updates via WebSocket
- Zustand for state management

## Getting Started

### Quick Start

1. **Start Docker services** (PostgreSQL + Redis):
   ```bash
   docker-compose up -d
   ```

2. **Setup backend**:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your API keys
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

3. **Setup frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Detailed Setup

- [Docker Setup Guide](DOCKER_SETUP.md) - PostgreSQL and Redis configuration
- [Backend README](backend/README.md) - API setup and configuration
- [Frontend README](frontend/README.md) - UI setup and configuration

## Database Migrations

This project uses Alembic for database migrations. If you encounter issues with missing data or empty tables:

### Quick Fix
```bash
cd backend
python alembic/scripts/check_migrations  # Check for issues
python alembic/scripts/verify_db          # Verify database state
```

### Learn More
- [DOCKER_SETUP.md](DOCKER_SETUP.md) - Docker and database management
- [backend/alembic/MIGRATIONS.md](backend/alembic/MIGRATIONS.md) - Migration guide and troubleshooting


