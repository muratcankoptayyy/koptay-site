"""
Automatically add CSRF tokens to all POST forms in templates
"""
import os
import re

templates_dir = 'templates'
added_count = 0
skipped_count = 0

def add_csrf_token(content):
    """Add CSRF token after form opening tag if not already present"""
    global added_count, skipped_count
    
    # Pattern: <form ... method="POST" ...> that doesn't already have csrf_token
    form_pattern = r'(<form[^>]*method=["\']POST["\'][^>]*>)(\s*)'
    
    def replace_form(match):
        global added_count, skipped_count
        form_tag = match.group(1)
        whitespace = match.group(2) if match.group(2) else '\n                    '
        
        # Check if there's already a csrf_token in the next 200 characters
        start_pos = match.start()
        check_area = content[start_pos:start_pos + 300]
        
        if 'csrf_token' in check_area:
            skipped_count += 1
            return match.group(0)  # Already has CSRF token
        
        # Add CSRF token
        added_count += 1
        csrf_input = '<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>'
        return form_tag + whitespace + csrf_input + whitespace
    
    return re.sub(form_pattern, replace_form, content)

# Process all HTML files
for root, dirs, files in os.walk(templates_dir):
    for filename in files:
        if filename.endswith('.html'):
            filepath = os.path.join(root, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file has POST forms
            if 'method="POST"' in content or "method='POST'" in content:
                original_added = added_count
                new_content = add_csrf_token(content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    forms_added = added_count - original_added
                    if forms_added > 0:
                        print(f"✅ {filepath}: {forms_added} form güncellendi")
                else:
                    print(f"⏭️  {filepath}: Zaten CSRF token var")

print(f"\n{'='*60}")
print(f"✨ Toplam {added_count} forma CSRF token eklendi")
print(f"⏭️  {skipped_count} form zaten CSRF token'a sahip")
print(f"{'='*60}")
