"""
Script to remove emoji from logger calls in app.py.
"""

import re
from pathlib import Path


def clean_emoji_from_logger_calls():
    """Remove emoji from all logger.xxx() calls in app.py."""
    app_file = Path(__file__).parent.parent / 'app.py'
    
    if not app_file.exists():
        print(f"❌ app.py not found at {app_file}")
        return
    
    print(f"📖 Reading {app_file}")
    content = app_file.read_text(encoding='utf-8')
    
    # Comprehensive emoji pattern
    emoji_pattern = r'[\U0001F300-\U0001F9FF]|[\U00002600-\U000027BF]|[\U0001F600-\U0001F64F]'
    
    # Count emojis before
    emojis_before = len(re.findall(emoji_pattern, content))
    print(f"🔍 Found {emojis_before} emojis in file")
    
    # Remove all emojis
    content_clean = re.sub(emoji_pattern, '', content)
    
    # Count emojis after
    emojis_after = len(re.findall(emoji_pattern, content_clean))
    
    # Write back
    app_file.write_text(content_clean, encoding='utf-8')
    
    print(f"✅ Emoji cleanup complete!")
    print(f"   Removed: {emojis_before - emojis_after} emojis")
    print(f"   Remaining: {emojis_after} emojis")


if __name__ == '__main__':
    clean_emoji_from_logger_calls()
