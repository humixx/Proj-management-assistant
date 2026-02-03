"""
Backend Startup Script

Checks database health before starting the server.
Use this instead of directly running uvicorn to catch issues early.

Usage:
    python start.py
    
Or for production:
    python start.py --host 0.0.0.0 --port 8000
"""

import asyncio
import sys
import subprocess
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

async def quick_db_check():
    """Quick database health check."""
    print("Checking database connection...")
    
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        
        async with engine.connect() as conn:
            # Check connection
            await conn.execute(text("SELECT 1"))
            
            # Check pgvector
            result = await conn.execute(
                text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            )
            if not result.scalar():
                print("[WARNING] pgvector extension not found!")
                print("          Run: docker exec pm_postgres psql -U postgres -d project_assistant -c 'CREATE EXTENSION vector;'")
            
            # Check tables
            result = await conn.execute(
                text("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'projects')")
            )
            if not result.scalar():
                print("[ERROR] Database tables not found!")
                print("        Run: alembic upgrade head")
                await engine.dispose()
                return False
            
            # Check migration version
            try:
                result = await conn.execute(text("SELECT version_num FROM alembic_version"))
                version = result.scalar()
                print(f"[OK] Database ready (migration: {version})")
            except:
                print("[WARNING] Alembic version table not found")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"[ERROR] Database check failed: {e}")
        print("\nPossible solutions:")
        print("  1. Start Docker services: docker-compose up -d")
        print("  2. Check DATABASE_URL in .env file")
        print("  3. Run: python verify_db.py")
        return False

def start_server(args):
    """Start the uvicorn server."""
    cmd = ["uvicorn", "app.main:app", "--reload"]
    cmd.extend(args)
    
    print(f"\nStarting server: {' '.join(cmd)}\n")
    print("="*60)
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)

def main():
    """Main startup sequence."""
    print("\n" + "="*60)
    print("BACKEND STARTUP")
    print("="*60 + "\n")
    
    # Quick database check
    if not asyncio.run(quick_db_check()):
        print("\n[ERROR] Database is not ready. Please fix the issues above.")
        sys.exit(1)
    
    # Start server
    args = sys.argv[1:]  # Pass through any command line arguments
    start_server(args)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStartup cancelled.")
        sys.exit(1)
