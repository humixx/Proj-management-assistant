# Docker Setup Guide

This project uses Docker for PostgreSQL (with pgvector) and Redis.

## Quick Start

### 1. Start Services

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Verify services are running
docker-compose ps
```

Expected output:
```
NAME         IMAGE                   STATUS
pm_postgres  pgvector/pgvector:pg16  Up
pm_redis     redis:7-alpine          Up
```

### 2. Verify Database Connection

```bash
cd backend
python alembic/scripts/verify_db
```

This will check:
- Database connectivity
- pgvector extension
- All required tables
- Data integrity

### 3. Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload
```

### 4. Start Frontend

```bash
cd frontend
npm run dev
```

## Docker Services

### PostgreSQL with pgvector

- **Image**: `pgvector/pgvector:pg16`
- **Container**: `pm_postgres`
- **Port**: `5432` (mapped to host)
- **Database**: `project_assistant`
- **User**: `postgres`
- **Password**: `postgres` (default)

The pgvector extension is pre-installed in this image and automatically enabled.

### Redis

- **Image**: `redis:7-alpine`
- **Container**: `pm_redis`
- **Port**: `6379` (mapped to host)

## Common Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Data
```bash
# WARNING: This will delete all data!
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# PostgreSQL only
docker-compose logs -f postgres

# Redis only
docker-compose logs -f redis
```

### Connect to PostgreSQL
```bash
# Using docker exec
docker exec -it pm_postgres psql -U postgres -d project_assistant

# Using psql from host (if installed)
psql -h localhost -U postgres -d project_assistant
```

### Connect to Redis
```bash
docker exec -it pm_redis redis-cli
```

## Database Management

### Check Database Tables
```bash
docker exec pm_postgres psql -U postgres -d project_assistant -c "\dt"
```

### Check Extensions
```bash
docker exec pm_postgres psql -U postgres -d project_assistant -c "\dx"
```

### Backup Database
```bash
docker exec pm_postgres pg_dump -U postgres project_assistant > backup.sql
```

### Restore Database
```bash
docker exec -i pm_postgres psql -U postgres -d project_assistant < backup.sql
```

## Troubleshooting

### Issue: "Port 5432 already in use"

**Cause**: Another PostgreSQL service is running on port 5432

**Solution**:
```bash
# Windows - Check what's using the port
netstat -ano | findstr :5432

# Stop local PostgreSQL service
# Option 1: Services (services.msc) - Find PostgreSQL and stop it
# Option 2: Command line
net stop postgresql-x64-17  # Adjust version as needed
```

### Issue: "Cannot connect to database"

**Solution**:
```bash
# Check if containers are running
docker-compose ps

# If not running, start them
docker-compose up -d

# Check container logs
docker-compose logs postgres
```

### Issue: "Data disappeared after restart"

**Cause**: Migration version mismatch or empty migration file applied

**Solution**:
```bash
# Check current migration version in database
docker exec pm_postgres psql -U postgres -d project_assistant -c "SELECT * FROM alembic_version;"

# Check migration files
cd backend
python check_migrations.py

# If version mismatch, update to current head
cd backend
alembic current  # See what Alembic expects
docker exec pm_postgres psql -U postgres -d project_assistant -c "UPDATE alembic_version SET version_num = 'VERSION_FROM_ALEMBIC_CURRENT';"
```

### Issue: "pgvector extension not found"

**Solution**:
```bash
# Enable pgvector extension
docker exec pm_postgres psql -U postgres -d project_assistant -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verify
docker exec pm_postgres psql -U postgres -d project_assistant -c "\dx"
```

## Data Persistence

Database data is stored in a Docker volume named `postgres_data`. This ensures:
- Data persists across container restarts
- Data survives `docker-compose down`
- Data is only lost with `docker-compose down -v`

### View Volumes
```bash
docker volume ls | findstr postgres
```

### Inspect Volume
```bash
docker volume inspect project-management-assistant_postgres_data
```

## Development vs Production

### Development (Current Setup)
- Direct port exposure (5432, 6379)
- Simple credentials
- Data in Docker volume

### Production Recommendations
1. **Use secrets management** for passwords
2. **Use environment-specific configs**
3. **Set up backups** (automated pg_dump)
4. **Use Docker networks** instead of exposed ports
5. **Enable SSL** for PostgreSQL
6. **Set up monitoring** (logs, metrics)

## Environment Variables

The `docker-compose.yml` supports environment variables:

```bash
# Create .env file in project root (not backend/.env)
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_NAME=project_assistant
```

Then update `backend/.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres:your_secure_password@localhost:5432/project_assistant
```

## Health Checks

Both services have health checks configured:

```bash
# Check health status
docker-compose ps

# Detailed health info
docker inspect pm_postgres --format='{{.State.Health.Status}}'
docker inspect pm_redis --format='{{.State.Health.Status}}'
```

## Migration Best Practices

1. **Always check migrations before applying**:
   ```bash
   cd backend
   python alembic/scripts/check_migrations
   ```

2. **Keep Alembic version in sync**:
   ```bash
   # After pulling code changes
   cd backend
   alembic upgrade head
   ```

3. **Never create empty migrations**:
   - Review auto-generated migrations
   - Delete files with only `pass` statements

4. **Backup before major migrations**:
   ```bash
   docker exec pm_postgres pg_dump -U postgres project_assistant > backup_before_migration.sql
   ```

## Quick Reference Card

| Task | Command |
|------|---------|
| Start services | `docker-compose up -d` |
| Stop services | `docker-compose down` |
| View logs | `docker-compose logs -f` |
| Connect to DB | `docker exec -it pm_postgres psql -U postgres -d project_assistant` |
| Check tables | `docker exec pm_postgres psql -U postgres -d project_assistant -c "\dt"` |
| Enable pgvector | `docker exec pm_postgres psql -U postgres -d project_assistant -c "CREATE EXTENSION IF NOT EXISTS vector;"` |
| Backup DB | `docker exec pm_postgres pg_dump -U postgres project_assistant > backup.sql` |
| Check migration | `cd backend && python alembic/scripts/check_migrations` |
| Verify DB | `cd backend && python alembic/scripts/verify_db` |

## Need Help?

1. Check this guide first
2. Run `docker-compose logs` to see error messages
3. Run `cd backend && python alembic/scripts/verify_db` to diagnose issues
4. Check [MIGRATIONS.md](backend/alembic/MIGRATIONS.md) for database migration issues

