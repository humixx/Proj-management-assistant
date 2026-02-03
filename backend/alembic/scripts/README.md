# Database Management Scripts

Helper scripts for database setup, verification, and migration management.

## Scripts Overview

### check_migrations.py
**Purpose**: Check migration files for common issues before applying them.

**Usage**:
```bash
cd backend
python alembic/scripts/check_migrations.py
```

**What it checks**:
- Empty upgrade() functions
- Empty downgrade() functions
- Duplicate "Initial migration" files

**When to use**: Before committing or applying migrations.

---

### verify_db.py
**Purpose**: Comprehensive database health check.

**Usage**:
```bash
cd backend
python alembic/scripts/verify_db.py
```

**What it checks**:
- Database connectivity
- pgvector extension status
- Required tables existence
- Migration version
- Table structure

**When to use**: 
- After setup
- When diagnosing issues
- Before starting server

---

### setup_db.py
**Purpose**: Initial database setup with pgvector extension and migrations.

**Usage**:
```bash
cd backend
python alembic/scripts/setup_db.py
```

**What it does**:
1. Enables pgvector extension
2. Runs all pending migrations
3. Verifies final state

**When to use**: First-time setup or after database reset.

---

### reset_db.py
**Purpose**: Interactive database reset with safety checks.

**Usage**:
```bash
cd backend
python alembic/scripts/reset_db.py
```

**What it does**:
1. Shows current migration state
2. Confirms with user
3. Runs migrations
4. Verifies final state

**When to use**: When experiencing migration issues or data inconsistencies.

---

## Quick Command Reference

| Task | Command |
|------|---------|
| Check migrations | `python alembic/scripts/check_migrations.py` |
| Verify database | `python alembic/scripts/verify_db.py` |
| Setup database | `python alembic/scripts/setup_db.py` |
| Reset database | `python alembic/scripts/reset_db.py` |

## File Location

All scripts are located in `backend/alembic/scripts/` and should be run from the `backend/` directory using the module syntax shown above.

## Adding New Scripts

When adding new database management scripts:

1. Place them in this directory
2. Follow the naming convention: `action_db.py`
3. Add module-level docstring explaining purpose
4. Update this README with usage instructions
5. Make scripts safe to run multiple times (idempotent)

## Best Practices

- Always run `verify_db.py` before and after migrations
- Use `check_migrations.py` before committing migration files
- Keep scripts simple and focused on one task
- Provide clear error messages with actionable solutions
- Log all operations for debugging
