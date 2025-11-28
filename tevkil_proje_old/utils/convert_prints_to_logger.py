"""
Script to convert print() statements to logger calls in app.py.

This script:
1. Scans app.py for print() statements
2. Determines appropriate log level based on emoji/keywords
3. Replaces print() with logger.level() calls
4. Adds logger import if not present
"""

import re
from pathlib import Path


def determine_log_level(print_content: str) -> str:
    """
    Determine appropriate log level based on print content.
    
    Returns: 'debug', 'info', 'warning', 'error', or 'critical'
    """
    content_lower = print_content.lower()
    
    # ERROR indicators
    if any(indicator in content_lower for indicator in ['❌', 'error', 'failed', 'failure', 'exception']):
        return 'error'
    
    # WARNING indicators
    if any(indicator in content_lower for indicator in ['⚠️', 'warning', 'uyari', 'could not', 'duplicate']):
        return 'warning'
    
    # DEBUG indicators (detailed technical info)
    if any(indicator in content_lower for indicator in ['[debug', 'checking', 'password', 'hash', 'length', 'session', 'query']):
        return 'debug'
    
    # SUCCESS/INFO indicators
    if any(indicator in content_lower for indicator in ['✅', 'success', 'başarı', 'created', 'connected', 'verified']):
        return 'info'
    
    # WebSocket/Webhook specific
    if any(indicator in content_lower for indicator in ['websocket', 'webhook', 'challenge', 'gönderen', 'mesaj']):
        return 'info'
    
    # Default to info
    return 'info'


def clean_print_content(content: str) -> str:
    """Remove emoji and clean up print content."""
    # Remove ALL emoji using comprehensive pattern
    # This pattern covers most common emoji ranges
    emoji_pattern = r'[\U0001F300-\U0001F9FF]|[\U00002600-\U000027BF]|[\U0001F600-\U0001F64F]'
    content = re.sub(emoji_pattern, '', content)
    
    # Remove [DEBUG prefix since logger adds it
    content = re.sub(r'\[DEBUG[^\]]*\]\s*', '', content)
    
    return content.strip()


def convert_print_to_logger(line: str, indentation: str) -> str:
    """Convert a single print() line to logger call."""
    # Extract print content
    match = re.search(r'print\((.*)\)', line)
    if not match:
        return line
    
    print_content = match.group(1)
    
    # Determine log level
    log_level = determine_log_level(print_content)
    
    # Clean content
    cleaned_content = clean_print_content(print_content)
    
    # Build logger call
    logger_call = f"{indentation}logger.{log_level}({cleaned_content})"
    
    return logger_call


def add_logger_import(content: str) -> str:
    """Add logger import at the top of the file if not present."""
    if 'from utils.logger import get_logger' in content:
        return content
    
    # Find where to insert (after other imports)
    lines = content.split('\n')
    
    # Find last import line
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith(('import ', 'from ')) and not line.strip().startswith('#'):
            last_import_idx = i
    
    # Insert logger import and initialization after last import
    insert_lines = [
        'from utils.logger import get_logger',
        '',
        'logger = get_logger(__name__)',
        ''
    ]
    
    lines = lines[:last_import_idx + 1] + insert_lines + lines[last_import_idx + 1:]
    
    return '\n'.join(lines)


def convert_app_py():
    """Main function to convert all prints in app.py to logger calls."""
    app_file = Path(__file__).parent.parent / 'app.py'
    
    if not app_file.exists():
        print(f"❌ app.py not found at {app_file}")
        return
    
    print(f"📖 Reading {app_file}")
    content = app_file.read_text(encoding='utf-8')
    
    # Add logger import
    print("📝 Adding logger import...")
    content = add_logger_import(content)
    
    # Convert all print statements
    lines = content.split('\n')
    converted_count = 0
    
    print("🔄 Converting print statements to logger calls...")
    for i, line in enumerate(lines):
        # Match print statements (preserve indentation)
        match = re.match(r'^(\s*)print\(', line)
        if match:
            indentation = match.group(1)
            converted_line = convert_print_to_logger(line, indentation)
            lines[i] = converted_line
            converted_count += 1
    
    # Write back
    new_content = '\n'.join(lines)
    
    # Create backup
    backup_file = app_file.with_suffix('.py.backup')
    print(f"💾 Creating backup at {backup_file}")
    app_file.write_text(content, encoding='utf-8')
    backup_file.write_text(content, encoding='utf-8')
    
    # Write converted file
    print(f"✍️ Writing converted file...")
    app_file.write_text(new_content, encoding='utf-8')
    
    print(f"✅ Conversion complete!")
    print(f"   📊 Converted {converted_count} print statements to logger calls")
    print(f"   💾 Backup saved to {backup_file}")
    print(f"\n📋 Next steps:")
    print(f"   1. Review the changes: git diff app.py")
    print(f"   2. Test the application")
    print(f"   3. If satisfied, delete backup: {backup_file}")


if __name__ == '__main__':
    convert_app_py()
