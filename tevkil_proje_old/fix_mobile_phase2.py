"""
Mobil-specific iyileştirmeler - 2. Aşama
Table'lar, formlar ve detay sayfaları için
"""
import os
import re

templates_dir = 'templates'
fixes_applied = {}

def add_table_responsiveness(content, filename):
    """Table'ları mobil uyumlu hale getir"""
    changes = []
    
    # 1. Table wrapper yoksa ekle
    if '<table' in content and 'overflow-x-auto' not in content:
        # Table'ları wrapper'a al
        content = re.sub(
            r'(<table[^>]*class="[^"]*")',
            r'<div class="overflow-x-auto -mx-4 sm:mx-0"><div class="inline-block min-w-full align-middle"><div class="overflow-hidden">\1',
            content
        )
        # Closing divler
        content = re.sub(
            r'(</table>)(\s*)(</div>)?',
            r'\1</div></div></div>\2\3',
            content,
            count=content.count('<table')
        )
        changes.append("table'lara responsive wrapper ekledi")
    
    # 2. Table cell padding mobilde küçült
    content = re.sub(
        r'(<t[dh][^>]*class="[^"]*)\bp-4\b([^"]*")',
        r'\1p-2 sm:p-4\2',
        content
    )
    
    # 3. Table text size mobilde küçült
    content = re.sub(
        r'(<t[dh][^>]*class="[^"]*)\btext-base\b([^"]*")',
        r'\1text-sm sm:text-base\2',
        content
    )
    
    if '<table' in content:
        changes.append("table padding ve text boyutlarını responsive yaptı")
    
    return content, changes

def add_form_responsiveness(content, filename):
    """Form elementlerini mobil uyumlu hale getir"""
    changes = []
    
    # 1. Form input height mobilde küçült
    content = re.sub(
        r'(<input[^>]*class="[^"]*)\bh-14\b([^"]*")',
        r'\1h-12 sm:h-14\2',
        content
    )
    
    # 2. Button'ları full-width yap mobilde
    if '<button' in content and 'w-full sm:w-auto' not in content:
        content = re.sub(
            r'(<button[^>]*class="(?![^"]*w-full)[^"]*)"',
            r'\1 w-full sm:w-auto"',
            content
        )
        changes.append("button'ları mobilde full-width yaptı")
    
    # 3. Label text boyutu
    content = re.sub(
        r'(<label[^>]*class="[^"]*)\btext-base\b([^"]*")',
        r'\1text-sm sm:text-base\2',
        content
    )
    
    return content, changes

def add_card_responsiveness(content, filename):
    """Card'ları mobil uyumlu hale getir"""
    changes = []
    
    # 1. Card shadow mobilde hafiflet
    content = re.sub(
        r'\bshadow-xl\b(?!\s+(?:md|sm|lg):)',
        r'shadow-md sm:shadow-xl',
        content
    )
    
    # 2. Card rounded corners mobilde küçült
    content = re.sub(
        r'\brounded-2xl\b(?!\s+(?:md|sm|lg):)',
        r'rounded-xl sm:rounded-2xl',
        content
    )
    
    if 'shadow' in content or 'rounded' in content:
        changes.append("card görünümünü mobil optimize etti")
    
    return content, changes

def add_image_responsiveness(content, filename):
    """Image'leri mobil uyumlu hale getir"""
    changes = []
    
    # 1. Image height sınırla
    if '<img' in content:
        content = re.sub(
            r'(<img[^>]*class="[^"]*)\bh-\d+\b([^"]*")',
            r'\1h-auto max-h-64 sm:max-h-96\2',
            content
        )
        changes.append("image boyutlarını mobil optimize etti")
    
    return content, changes

def add_spacing_optimizations(content, filename):
    """Spacing'leri mobil optimize et"""
    changes = []
    
    # 1. Section spacing
    content = re.sub(r'\bspace-y-8\b(?!\s+(?:md|sm|lg):)', r'space-y-4 sm:space-y-8', content)
    content = re.sub(r'\bspace-x-8\b(?!\s+(?:md|sm|lg):)', r'space-x-4 sm:space-x-8', content)
    
    # 2. Margin bottom büyük değerler
    content = re.sub(r'\bmb-12\b(?!\s+(?:md|sm|lg):)', r'mb-6 sm:mb-12', content)
    content = re.sub(r'\bmb-10\b(?!\s+(?:md|sm|lg):)', r'mb-5 sm:mb-10', content)
    
    # 3. Margin top büyük değerler
    content = re.sub(r'\bmt-12\b(?!\s+(?:md|sm|lg):)', r'mt-6 sm:mt-12', content)
    content = re.sub(r'\bmt-10\b(?!\s+(?:md|sm|lg):)', r'mt-5 sm:mt-10', content)
    
    if any(x in content for x in ['space-y', 'space-x', 'mb-', 'mt-']):
        changes.append("spacing değerlerini mobil optimize etti")
    
    return content, changes

# Process all HTML files
for root, dirs, files in os.walk(templates_dir):
    for filename in files:
        if filename.endswith('.html'):
            filepath = os.path.join(root, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                file_changes = []
                
                # Apply all fixes
                content, changes = add_table_responsiveness(content, filename)
                file_changes.extend(changes)
                
                content, changes = add_form_responsiveness(content, filename)
                file_changes.extend(changes)
                
                content, changes = add_card_responsiveness(content, filename)
                file_changes.extend(changes)
                
                content, changes = add_image_responsiveness(content, filename)
                file_changes.extend(changes)
                
                content, changes = add_spacing_optimizations(content, filename)
                file_changes.extend(changes)
                
                if content != original_content and file_changes:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    fixes_applied[filename] = file_changes
                    print(f"✅ {filename}:")
                    for change in file_changes:
                        print(f"   • {change}")
                elif content != original_content:
                    print(f"⚠️  {filename}: Değişti ama spesifik fix yok")
                else:
                    print(f"⏭️  {filename}: Zaten optimize")
                    
            except Exception as e:
                print(f"❌ {filename}: Hata - {str(e)}")

print(f"\n{'='*70}")
print(f"📱 Mobil Optimizasyon Özeti (2. Aşama):")
print(f"   ✅ {len(fixes_applied)} dosya güncellendi")
print(f"{'='*70}")

if fixes_applied:
    print(f"\n📋 Yapılan İyileştirmeler:")
    all_changes = {}
    for changes in fixes_applied.values():
        for change in changes:
            all_changes[change] = all_changes.get(change, 0) + 1
    
    for change, count in sorted(all_changes.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {change}: {count} dosya")
