# Troubleshooting Guide

Common issues and their solutions.

## Database Issues

### Issue: "All data in database is gone" / Empty tables

**Symptoms:**
- Projects list shows no data
- All tables appear empty
- Recently worked fine, now broken

**Causes:**
1. Empty migration file was applied
2. Migration version mismatch
3. Wrong database connection

**Solution:**

1. **Check which database you're connected to:**
   ```bash
   cd backend
   python alembic/scripts/verify_db
   ```

2. **If using Docker (recommended):**
   ```bash
   # Check if Docker containers are running
   docker-compose ps
   
   # Check data in Docker database
   docker exec pm_postgres psql -U postgres -d project_assistant -c "SELECT COUNT(*) FROM projects;"
   
   # If data is there, check migration version
   docker exec pm_postgres psql -U postgres -d project_assistant -c "SELECT * FROM alembic_version;"
   
   # Compare with expected version
   cd backend
   alembic current
   
   # If versions don't match, update database version
   docker exec pm_postgres psql -U postgres -d project_assistant -c "UPDATE alembic_version SET version_num = 'VERSION_FROM_ALEMBIC_CURRENT';"
   ```

3. **Check for empty migration files:**
   ```bash
   cd backend
   python alembic/scripts/check_migrations
   ```
   
   If you find empty migrations (files with only `pass` statements), delete them:
   ```bash
   # Delete the empty migration file
   rm alembic/versions/EMPTY_MIGRATION_FILE.py
   ```

4. **Verify database is working:**
   ```bash
   cd backend
   python alembic/scripts/verify_db
   python start.py  # This checks database before starting server
   ```

### Issue: "pgvector extension not found"

**Solution:**
```bash
# Enable pgvector in Docker container
docker exec pm_postgres psql -U postgres -d project_assistant -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verify
docker exec pm_postgres psql -U postgres -d project_assistant -c "\dx"
```

### Issue: "Cannot connect to database"

**Symptoms:**
- `CONNECTION REFUSED` errors
- Server won't start
- Database timeout errors

**Solution:**

1. **Check if Docker containers are running:**
   ```bash
   docker-compose ps
   ```
   
   If not running:
   ```bash
   docker-compose up -d
   ```

2. **Check if local PostgreSQL is conflicting:**
   ```bash
   # Windows
   netstat -ano | findstr :5432
   
   # If local PostgreSQL is running, stop it
   net stop postgresql-x64-17  # Adjust version
   ```

3. **Verify DATABASE_URL in .env:**
   ```bash
   # Should point to Docker container
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/project_assistant
   ```

4. **Check Docker logs:**
   ```bash
   docker-compose logs postgres
   ```

## Migration Issues

### Issue: "Migration version mismatch"

**Solution:**
```bash
# Check current version in database
docker exec pm_postgres psql -U postgres -d project_assistant -c "SELECT * FROM alembic_version;"

# Check expected version
cd backend
alembic current

# If they don't match, update database to match
docker exec pm_postgres psql -U postgres -d project_assistant -c "UPDATE alembic_version SET version_num = 'EXPECTED_VERSION';"
```

### Issue: "Empty migration created"

**Symptoms:**
- Migration file has only `pass` in upgrade() function
- No actual database changes
- Auto-generated but empty

**Prevention:**
1. Always review migration files before committing
2. Run `python check_migrations.py` before applying
3. Delete empty migrations immediately

**Solution:**
```bash
# Check for empty migrations
cd backend
python alembic/scripts/check_migrations

# Delete empty migration files manually
# Then ensure version is correct
alembic current
docker exec pm_postgres psql -U postgres -d project_assistant -c "UPDATE alembic_version SET version_num = 'CORRECT_VERSION';"
```

## Docker Issues

### Issue: "Port already in use"

**Symptoms:**
- `docker-compose up` fails
- Error: "bind: address already in use"

**Solution:**
```bash
# Find what's using the port
netstat -ano | findstr :5432  # For PostgreSQL
netstat -ano | findstr :6379  # For Redis

# Stop local services
net stop postgresql-x64-17  # PostgreSQL
# or use Services (services.msc) to stop manually

# Then start Docker services
docker-compose up -d
```

### Issue: "Cannot start Docker services"

**Solution:**
```bash
# Check Docker Desktop is running

# Check logs
docker-compose logs

# Try recreating containers
docker-compose down
docker-compose up -d --force-recreate

# If still failing, check disk space and Docker resources
```

## Frontend Issues

### Issue: "Cannot connect to backend"

**Solution:**

1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/docs
   # Should return HTML
   ```

2. **Check NEXT_PUBLIC_API_URL in frontend/.env:**
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Check CORS settings in backend:**
   - Should allow `http://localhost:3000`

### Issue: "Environment variables not loading"

**Solution:**

1. **Frontend:**
   - Environment variables must start with `NEXT_PUBLIC_` to be available in browser
   - Restart dev server after changing .env
   ```bash
   # Stop the server (Ctrl+C)
   npm run dev
   ```

2. **Backend:**
   - Restart uvicorn after changing .env
   ```bash
   # Stop the server (Ctrl+C)
   python start.py
   ```

## Server Issues

### Issue: "Server starts but endpoints return errors"

**Solution:**

1. **Check database tables exist:**
   ```bash
   cd backend
   python alembic/scripts/verify_db
   ```

2. **Check migrations are applied:**
   ```bash
   cd backend
   alembic current
   alembic upgrade head
   ```

3. **Check logs for specific errors:**
   - Look at terminal output
   - Check for missing API keys in .env

### Issue: "Slow response times"

**Possible causes:**
1. Redis not running
2. Database needs indexing
3. Large document processing

**Solution:**
```bash
# Check Redis
docker-compose ps
docker exec pm_redis redis-cli PING
# Should return: PONG

# Restart services
docker-compose restart

# Check database indexes
docker exec pm_postgres psql -U postgres -d project_assistant -c "\di"
```

## API Key Issues

### Issue: "Voyage AI / Anthropic API errors"

**Solution:**

1. **Check API keys in backend/.env:**
   ```bash
   VOYAGE_API_KEY=your_actual_key_here
   ANTHROPIC_API_KEY=your_actual_key_here
   ```

2. **Verify keys are valid:**
   - Log in to respective platforms
   - Check key permissions
   - Generate new keys if needed

3. **Restart server after updating keys**

## Quick Diagnostic Commands

Run these to quickly diagnose issues:

```bash
# Check Docker services
docker-compose ps

# Check database
cd backend
python alembic/scripts/verify_db

# Check migrations
cd backend
python alembic/scripts/check_migrations
alembic current

# Check backend can start
cd backend
python start.py

# Check frontend can start
cd frontend
npm run dev
```

## Still Having Issues?

1. **Read the relevant guide:**
   - [DOCKER_SETUP.md](DOCKER_SETUP.md) for Docker issues
   - [backend/alembic/MIGRATIONS.md](backend/alembic/MIGRATIONS.md) for migration issues
   - [backend/README.md](backend/README.md) for backend setup

2. **Check logs:**
   ```bash
   # Docker logs
   docker-compose logs -f
   
   # Backend logs
   # (visible in terminal where you run uvicorn)
   
   # Frontend logs
   # (visible in terminal where you run npm run dev)
   ```

3. **Nuclear option (last resort):**
   ```bash
   # CAUTION: This will delete all data!
   docker-compose down -v
   docker-compose up -d
   cd backend
   alembic upgrade head
   # You'll need to recreate all data
   ```

