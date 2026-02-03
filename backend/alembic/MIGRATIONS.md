# Database Migrations Guide

## Overview

This project uses Alembic for database migrations. This guide will help you avoid common migration issues.

## ⚠️ Common Issue: Data Loss After Migration

### Problem
If you notice that your database tables are empty after running migrations, it's likely due to:
1. **Empty migration files** - Migration files with only `pass` statements that don't create tables
2. **Out-of-sync migrations** - The database thinks migrations are applied but tables don't exist

### Solution
Run the reset script:

```bash
cd backend
python reset_db.py
```

This will verify and fix your migration state without losing data.

## Best Practices

### 1. Creating New Migrations

**✅ DO THIS:**
```bash
# After changing models, create a migration
alembic revision --autogenerate -m "descriptive message"

# Review the generated migration file BEFORE applying
# Check that it has actual commands, not just "pass"

# Apply the migration
alembic upgrade head
```

**❌ DON'T DO THIS:**
```bash
# Don't run autogenerate multiple times without checking the result
alembic revision --autogenerate -m "initial"  # Creates migration
alembic revision --autogenerate -m "initial"  # Creates ANOTHER migration (might be empty!)
```

### 2. Before Applying Migrations

**Always check the migration file:**

```python
def upgrade() -> None:
    # ✅ Good - Has actual commands
    op.create_table('projects', ...)
    
    # ❌ Bad - Empty migration
    pass
```

**If you find an empty migration:**
1. Delete it immediately
2. Don't run `alembic upgrade head` with empty migrations

### 3. Checking Migration State

```bash
# See current migration version
alembic current

# See all migrations
alembic history

# See what would be applied
alembic upgrade head --sql
```

## Common Commands

### Reset Database (Safe)
```bash
python reset_db.py
```

### Create New Migration
```bash
# After modifying models in app/db/models.py
alembic revision --autogenerate -m "add new column to tasks"

# Review the file in alembic/versions/
# Then apply it
alembic upgrade head
```

### Rollback Migration
```bash
# Go back one migration
alembic downgrade -1

# Go to specific migration
alembic downgrade <revision_id>
```

### View Migration History
```bash
alembic history --verbose
```

## Troubleshooting

### Issue: "All data is gone"

**Cause:** Empty migration file was applied

**Fix:**
```bash
cd backend
python reset_db.py
```

### Issue: "Migration doesn't match database"

**Cause:** Models changed but migration wasn't created

**Fix:**
```bash
# Create a new migration
alembic revision --autogenerate -m "sync database with models"

# Review the file, then apply
alembic upgrade head
```

### Issue: "Can't generate new migrations"

**Cause:** Alembic might be confused about current state

**Fix:**
```bash
# Check current state
alembic current

# Check what Alembic sees
alembic history

# If needed, stamp to correct version
alembic stamp head
```

## Directory Structure

```
backend/
├── alembic/
│   ├── versions/          # Migration files go here
│   │   └── 8758f38f0950_initial_migration.py
│   ├── env.py            # Alembic configuration
│   └── script.py.mako    # Migration template
├── alembic.ini           # Alembic settings
├── reset_db.py          # Database reset helper script
└── MIGRATIONS.md         # This file
```

## Model Changes Workflow

1. **Modify your models** in `app/db/models.py`
2. **Generate migration**: `alembic revision --autogenerate -m "description"`
3. **Review migration file** in `alembic/versions/`
4. **Check for empty migrations** - delete if found
5. **Apply migration**: `alembic upgrade head`
6. **Verify**: `alembic current`
7. **Test**: Restart your server and check database

## Prevention Checklist

Before committing migrations:

- [ ] Migration file has actual commands (not just `pass`)
- [ ] Migration tested locally
- [ ] `alembic current` shows correct version
- [ ] Database tables exist and have data
- [ ] Server starts without errors

## Quick Reference

| Command | Description |
|---------|-------------|
| `python reset_db.py` | Fix migration issues safely |
| `alembic current` | Show current migration |
| `alembic history` | Show all migrations |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic downgrade -1` | Rollback one migration |
| `alembic revision --autogenerate -m "msg"` | Create new migration |

## Need Help?

If you continue to have issues:
1. Check this guide first
2. Run `python reset_db.py`
3. Check the migration files in `alembic/versions/`
4. Make sure only one "initial" migration exists
5. Verify your DATABASE_URL in `.env` is correct
