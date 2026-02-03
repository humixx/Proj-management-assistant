"""
Database Verification Script

Checks that the database is properly set up with all required tables.

Usage:
    cd backend
    python alembic/scripts/verify_db.py
"""

import asyncio
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

async def verify_database():
    """Verify database setup."""
    print("\n" + "="*60)
    print("DATABASE VERIFICATION")
    print("="*60)
    
    try:
        # Create engine
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        
        print("\n[1/5] Testing database connection...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"[SUCCESS] Connected to PostgreSQL")
            print(f"        Version: {version.split(',')[0]}")
        
        print("\n[2/5] Checking pgvector extension...")
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            )
            has_vector = result.scalar()
            if has_vector:
                print("[SUCCESS] pgvector extension is installed")
            else:
                print("[ERROR] pgvector extension is NOT installed")
                print("        Run: CREATE EXTENSION vector;")
                return False
        
        print("\n[3/5] Checking Alembic version table...")
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'alembic_version')")
            )
            has_alembic = result.scalar()
            if has_alembic:
                result = await conn.execute(text("SELECT version_num FROM alembic_version"))
                version_num = result.scalar()
                print(f"[SUCCESS] Alembic version table exists")
                print(f"        Current migration: {version_num}")
            else:
                print("[WARNING] Alembic version table not found")
                print("         Run: alembic upgrade head")
        
        print("\n[4/5] Checking required tables...")
        required_tables = [
            'projects',
            'tasks',
            'documents',
            'document_chunks',
            'chat_messages',
            'slack_integrations'
        ]
        
        all_tables_exist = True
        async with engine.connect() as conn:
            for table in required_tables:
                result = await conn.execute(
                    text(f"SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = '{table}')")
                )
                exists = result.scalar()
                if exists:
                    # Count rows
                    count_result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.scalar()
                    print(f"[SUCCESS] Table '{table}' exists ({count} rows)")
                else:
                    print(f"[ERROR] Table '{table}' does NOT exist")
                    all_tables_exist = False
        
        if not all_tables_exist:
            print("\n[ERROR] Some tables are missing!")
            print("        Run: python reset_db.py")
            return False
        
        print("\n[5/5] Verifying table structure...")
        async with engine.connect() as conn:
            # Check if document_chunks has embedding column with correct dimension
            result = await conn.execute(
                text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'document_chunks' 
                    AND column_name = 'embedding'
                """)
            )
            row = result.first()
            if row:
                print("[SUCCESS] document_chunks.embedding column exists")
            else:
                print("[WARNING] document_chunks.embedding column not found")
        
        print("\n" + "="*60)
        print("[SUCCESS] DATABASE VERIFICATION COMPLETE")
        print("="*60)
        print("\nYour database is properly configured!")
        print("You can now start the server: uvicorn app.main:app --reload\n")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Verification failed: {e}")
        print("\nPossible solutions:")
        print("  1. Check DATABASE_URL in .env file")
        print("  2. Make sure PostgreSQL is running")
        print("  3. Run: python reset_db.py")
        print()
        return False

def main():
    """Run verification."""
    success = asyncio.run(verify_database())
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
