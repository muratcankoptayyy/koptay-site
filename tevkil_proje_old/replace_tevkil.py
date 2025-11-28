import os
import glob

def replace_in_file(file_path):
    """Replace 'Tevkil Ağı' with 'Ulusal Tevkil Ağı Projesi' in a file"""
    try:
        # Read file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if replacement is needed
        if 'Tevkil Ağı' not in content:
            return False
        
        # Perform replacement
        new_content = content.replace('Tevkil Ağı', 'Ulusal Tevkil Ağı Projesi')
        
        # Write back with UTF-8 encoding
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"❌ Hata: {file_path} - {e}")
        return False

# Find all HTML files in templates directory
html_files = glob.glob('templates/**/*.html', recursive=True)

updated_count = 0
for file_path in html_files:
    if replace_in_file(file_path):
        print(f"✅ {file_path} güncellendi")
        updated_count += 1

print(f"\n✨ Toplam {updated_count} dosya güncellendi!")
