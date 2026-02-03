"""
Database Reset Script

This script helps reset the database to a clean state with proper migrations.
Use this if you encounter migration issues or empty database tables.

Usage:
    cd backend
    python alembic/scripts/reset_db.py
"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and print the result."""
    print(f"\n{'='*60}")
    print(f"[TASK] {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print(f"[ERROR] Command failed with return code {result.returncode}")
        return False
    
    print(f"[SUCCESS] {description} completed successfully")
    return True

def main():
    """Main reset sequence."""
    print("\n" + "="*60)
    print("DATABASE RESET SCRIPT")
    print("="*60)
    print("\n[WARNING] This will reset your database to a clean state.")
    print("[WARNING] All data will be preserved, but migrations will be verified.")
    
    response = input("\nDo you want to continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("[CANCELLED] Reset cancelled.")
        return
    
    # Step 1: Check current migration state
    if not run_command(
        "alembic current",
        "Checking current migration state"
    ):
        print("\n[WARNING] Could not determine current migration state.")
    
    # Step 2: Show migration history
    if not run_command(
        "alembic history",
        "Showing migration history"
    ):
        print("\n[WARNING] Could not show migration history.")
    
    # Step 3: Upgrade to head
    print("\n" + "="*60)
    print("Applying migrations...")
    print("="*60)
    
    if run_command(
        "alembic upgrade head",
        "Upgrading to latest migration"
    ):
        print("\n[SUCCESS] Database is now up to date!")
    else:
        print("\n[ERROR] Migration failed. Please check the errors above.")
        return
    
    # Step 4: Verify final state
    run_command(
        "alembic current",
        "Verifying final migration state"
    )
    
    print("\n" + "="*60)
    print("[SUCCESS] DATABASE RESET COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("   1. Restart your backend server (uvicorn app.main:app --reload)")
    print("   2. Your database should now be in the correct state")
    print("   3. If you still see issues, check the alembic/versions folder")
    print("      for any empty migration files and delete them.")
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Reset cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        sys.exit(1)
