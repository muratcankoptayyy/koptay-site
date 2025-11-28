"""
Fix deprecated datetime.utcnow() usage across the codebase.

This script replaces all instances of datetime.utcnow() with 
datetime.now(timezone.utc) to comply with Python 3.12+ standards.
"""

import re
from pathlib import Path
from typing import List, Tuple


def fix_datetime_in_file(file_path: Path) -> Tuple[int, List[str]]:
    """
    Replace datetime.utcnow() with datetime.now(timezone.utc) in a file.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        Tuple of (number of changes, list of change descriptions)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return 0, []
    
    original_content = content
    changes = []
    
    # Pattern 1: datetime.utcnow() → datetime.now(timezone.utc)
    pattern_utcnow = r'datetime\.utcnow\(\)'
    if re.search(pattern_utcnow, content):
        count = len(re.findall(pattern_utcnow, content))
        content = re.sub(pattern_utcnow, 'datetime.now(timezone.utc)', content)
        changes.append(f"Replaced {count}x datetime.utcnow()")
    
    # Pattern 2: Ensure timezone is imported
    has_datetime_import = 'from datetime import datetime' in content
    has_timezone_import = 'from datetime import' in content and 'timezone' in content
    
    if has_datetime_import and not has_timezone_import:
        # Add timezone to existing import
        content = re.sub(
            r'from datetime import datetime\b',
            'from datetime import datetime, timezone',
            content,
            count=1
        )
        changes.append("Added timezone to datetime import")
    elif 'datetime.now(timezone.utc)' in content and 'from datetime import' not in content:
        # Add full import if missing
        first_import = re.search(r'^(from |import )', content, re.MULTILINE)
        if first_import:
            insert_pos = first_import.start()
            content = (
                content[:insert_pos] +
                'from datetime import datetime, timezone\n' +
                content[insert_pos:]
            )
            changes.append("Added datetime import")
    
    # Save if changed
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return len(changes), changes
        except Exception as e:
            print(f"❌ Error writing {file_path}: {e}")
            return 0, []
    
    return 0, []


def main():
    """Fix all Python files in the project."""
    
    # Files to check
    files_to_check = [
        'app.py',
        'models.py',
        'security_utils.py',
        'whatsapp_central_bot.py',
        'whatsapp_meta_api.py',
        'whatsapp_bot.py',
        'email_service.py',
        'sms_service.py',
        'firebase_notification_service.py',
        'udf_service.py',
        'udf_service_dynamic.py',
        'spam_detector.py',
    ]
    
    # Also check utils directory
    utils_dir = Path('utils')
    if utils_dir.exists():
        files_to_check.extend([
            str(f) for f in utils_dir.glob('*.py')
        ])
    
    # Check tevkil directory
    tevkil_dir = Path('tevkil')
    if tevkil_dir.exists():
        files_to_check.extend([
            str(f) for f in tevkil_dir.glob('*.py')
        ])
    
    total_files_changed = 0
    total_changes = 0
    
    print("🔧 Starting datetime.utcnow() deprecation fix...\n")
    
    for file_str in files_to_check:
        file_path = Path(file_str)
        if not file_path.exists():
            continue
        
        count, changes = fix_datetime_in_file(file_path)
        
        if count > 0:
            total_files_changed += 1
            total_changes += count
            print(f"✅ {file_path}")
            for change in changes:
                print(f"   - {change}")
    
    print(f"\n🎉 Summary:")
    print(f"   - Files modified: {total_files_changed}")
    print(f"   - Total changes: {total_changes}")
    
    if total_changes == 0:
        print("   - No datetime.utcnow() usage found!")
    else:
        print("\n⚠️  Please review changes and run tests before committing!")


if __name__ == '__main__':
    main()
