# Quick Start Guide

Get up and running in 5 minutes.

## Prerequisites

- Docker Desktop installed and running
- Node.js 18+ and npm
- Python 3.11+

## Setup (First Time)

### 1. Start Docker Services

```bash
# From project root
docker-compose up -d
```

Wait 10 seconds for services to be ready.

### 2. Setup Backend

```bash
cd backend

# Create virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your API keys:
# - VOYAGE_API_KEY
# - ANTHROPIC_API_KEY

# Run migrations
alembic upgrade head

# Verify database
python alembic/scripts/verify_db
```

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment (if needed)
copy .env.example .env.local
```

### 4. Start Servers

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
python start.py
```

Backend will be at: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Frontend will be at: http://localhost:3000

## Daily Usage

After the first-time setup, you only need:

```bash
# Terminal 1 - Ensure Docker is running
docker-compose ps

# If not running:
docker-compose up -d

# Terminal 2 - Backend
cd backend
venv\Scripts\activate
python start.py

# Terminal 3 - Frontend
cd frontend
npm run dev
```

## Verify Everything Works

Visit: http://localhost:3000

You should see:
- Projects page
- Ability to create new project
- Chat interface
- Task management

## Common Issues

### "Database not found"
```bash
docker-compose up -d
cd backend
alembic upgrade head
```

### "Data is missing"
```bash
cd backend
python alembic/scripts/verify_db
# Follow the suggestions from the output
```

### "Port already in use"
```bash
# Stop local PostgreSQL service
net stop postgresql-x64-17

# Restart Docker
docker-compose restart
```

For more issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## API Keys

You need these API keys in `backend/.env`:

1. **Voyage AI** (for embeddings):
   - Sign up at: https://www.voyageai.com/
   - Get API key from dashboard
   - Add to .env: `VOYAGE_API_KEY=your_key_here`

2. **Anthropic Claude** (for AI chat):
   - Sign up at: https://console.anthropic.com/
   - Create API key
   - Add to .env: `ANTHROPIC_API_KEY=your_key_here`

## Slack Integration (Optional)

To enable Slack integration:

1. Create Slack app at: https://api.slack.com/apps
2. Get Client ID and Secret
3. Add to `backend/.env`:
   ```
   SLACK_CLIENT_ID=your_client_id
   SLACK_CLIENT_SECRET=your_secret
   ```

## Project Structure

```
project-management-assistant/
├── backend/           # FastAPI backend
│   ├── app/          # Application code
│   ├── alembic/      # Database migrations
│   └── .env          # Configuration
├── frontend/         # Next.js frontend
│   ├── src/          # Source code
│   └── .env.local    # Configuration
└── docker-compose.yml # Docker services
```

## Next Steps

- Read [backend/README.md](backend/README.md) for backend details
- Read [DOCKER_SETUP.md](DOCKER_SETUP.md) for Docker management
- Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if you hit issues

## Quick Commands Reference

| Task | Command |
|------|---------|
| Start Docker | `docker-compose up -d` |
| Stop Docker | `docker-compose down` |
| Start Backend | `cd backend && python start.py` |
| Start Frontend | `cd frontend && npm run dev` |
| Check Database | `cd backend && python alembic/scripts/verify_db` |
| Run Migrations | `cd backend && alembic upgrade head` |
| View Docker Logs | `docker-compose logs -f` |
| View API Docs | http://localhost:8000/docs |

## Need Help?

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Run diagnostic: `cd backend && python alembic/scripts/verify_db`
3. Check Docker: `docker-compose logs`

