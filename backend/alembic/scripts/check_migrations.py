"""
Migration Checker Script

This script checks for common migration issues before applying them.
Run this before committing or deploying migration changes.

Usage:
    cd backend
    python alembic/scripts/check_migrations.py
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

def find_migration_files() -> List[Path]:
    """Find all migration files."""
    # Script is now in alembic/scripts, so go up one level then into versions
    migrations_dir = Path(__file__).parent.parent / "versions"
    return sorted(migrations_dir.glob("*.py"))

def check_migration_file(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Check a migration file for common issues.
    
    Returns:
        (is_valid, list_of_issues)
    """
    issues = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for empty upgrade function
    upgrade_match = re.search(r'def upgrade\(\).*?:\s*#[^\n]*\n(.*?)def downgrade', content, re.DOTALL)
    if upgrade_match:
        upgrade_body = upgrade_match.group(1).strip()
        # Remove comments
        upgrade_body = re.sub(r'#.*?\n', '', upgrade_body)
        upgrade_body = upgrade_body.strip()
        
        if upgrade_body == 'pass' or not upgrade_body:
            issues.append("[WARNING] Empty upgrade() function - this migration does nothing!")
    
    # Check for empty downgrade function
    downgrade_match = re.search(r'def downgrade\(\).*?:\s*#[^\n]*\n(.*?)$', content, re.DOTALL)
    if downgrade_match:
        downgrade_body = downgrade_match.group(1).strip()
        downgrade_body = re.sub(r'#.*?\n', '', downgrade_body)
        downgrade_body = downgrade_body.strip()
        
        if downgrade_body == 'pass' or not downgrade_body:
            issues.append("[WARNING] Empty downgrade() function - cannot rollback this migration!")
    
    # Check for duplicate "Initial migration" titles
    if "Initial migration" in content:
        issues.append("[INFO] This is marked as 'Initial migration' - make sure there's only one!")
    
    return len(issues) == 0, issues

def main():
    """Main checker function."""
    print("\n" + "="*60)
    print("MIGRATION FILE CHECKER")
    print("="*60)
    
    migration_files = find_migration_files()
    
    if not migration_files:
        print("\n[ERROR] No migration files found!")
        return
    
    print(f"\nFound {len(migration_files)} migration file(s)\n")
    
    all_valid = True
    critical_issues = []
    
    for file_path in migration_files:
        print(f"Checking: {file_path.name}")
        is_valid, issues = check_migration_file(file_path)
        
        if not is_valid:
            all_valid = False
            print(f"  [ISSUES FOUND]")
            for issue in issues:
                print(f"     {issue}")
                if "Empty upgrade()" in issue:
                    critical_issues.append((file_path.name, issue))
        else:
            print(f"  [OK] Looks good")
        print()
    
    print("="*60)
    
    if critical_issues:
        print("\n[CRITICAL] ISSUES FOUND:\n")
        for filename, issue in critical_issues:
            print(f"  File: {filename}")
            print(f"  Issue: {issue}")
            print(f"  Fix: Delete this file or add proper migration commands\n")
        print("="*60)
        print("\n[ERROR] Please fix the issues above before applying migrations!")
        return 1
    
    if all_valid:
        print("\n[SUCCESS] All migration files look good!")
        print("\nYou can safely run: alembic upgrade head")
    else:
        print("\n[WARNING] Some warnings found, but no critical issues.")
        print("Review the warnings above before proceeding.")
    
    print()
    return 0 if all_valid else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
