"""
Database Setup Script

Enables pgvector extension and runs migrations.
Use this for initial database setup or when fixing migration issues.

Usage:
    cd backend
    python alembic/scripts/setup_db.py
"""

import asyncio
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
import subprocess

async def enable_pgvector():
    """Enable pgvector extension."""
    print("\n" + "="*60)
    print("DATABASE SETUP")
    print("="*60)
    
    try:
        print("\n[1/3] Connecting to database...")
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        
        async with engine.connect() as conn:
            print("[SUCCESS] Connected to database")
            
            print("\n[2/3] Enabling pgvector extension...")
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.commit()
            print("[SUCCESS] pgvector extension enabled")
            
            # Verify
            result = await conn.execute(
                text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            )
            if result.scalar():
                print("[SUCCESS] pgvector extension verified")
            else:
                print("[ERROR] pgvector extension not found after installation")
                return False
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to enable pgvector: {e}")
        return False

def run_migrations():
    """Run Alembic migrations."""
    print("\n[3/3] Running database migrations...")
    
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if result.returncode == 0:
        print("[SUCCESS] Migrations applied successfully")
        return True
    else:
        print(f"[ERROR] Migration failed with return code {result.returncode}")
        return False

async def main():
    """Main setup sequence."""
    # Enable pgvector
    if not await enable_pgvector():
        print("\n[ERROR] Failed to enable pgvector extension")
        print("Make sure your PostgreSQL has pgvector installed")
        return False
    
    # Run migrations
    if not run_migrations():
        print("\n[ERROR] Failed to apply migrations")
        return False
    
    print("\n" + "="*60)
    print("[SUCCESS] DATABASE SETUP COMPLETE")
    print("="*60)
    print("\nYour database is ready!")
    print("Start the server: uvicorn app.main:app --reload\n")
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[CANCELLED] Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Setup failed: {e}")
        sys.exit(1)
