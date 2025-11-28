"""
Mobil uyumluluk sorunlarını otomatik tespit ve düzeltme
"""
import os
import re

templates_dir = 'templates'
fixes_applied = {}

def fix_mobile_issues(content, filename):
    """Yaygın mobil uyumluluk sorunlarını düzelt"""
    changes = []
    original_content = content
    
    # 1. Min-width sorunları - mobilde taşma yapabilir
    if re.search(r'min-w-\[(?:400|500|600|700|800)px\]', content):
        content = re.sub(r'min-w-\[([4-8]\d\d)px\]', r'min-w-0 sm:min-w-[\1px]', content)
        changes.append("min-width değerlerini responsive yaptı")
    
    # 2. Fixed width'ler - mobilde taşma
    if re.search(r'w-\[(?:400|500|600|700|800)px\]', content):
        content = re.sub(r'w-\[([4-8]\d\d)px\]', r'w-full sm:w-[\1px]', content)
        changes.append("sabit width'leri responsive yaptı")
    
    # 3. Max-width yoksa ekle (container'lar için)
    if 'max-w-7xl' not in content and 'layout-container' in content:
        content = re.sub(
            r'(class="[^"]*layout-container[^"]*)"',
            r'\1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"',
            content
        )
        changes.append("container'lara max-width ekledi")
    
    # 4. Text size'ları responsive yap
    # text-4xl -> text-2xl md:text-4xl
    content = re.sub(r'\btext-4xl\b(?!\s+(?:md|sm|lg):)', r'text-2xl md:text-4xl', content)
    # text-3xl -> text-xl md:text-3xl
    content = re.sub(r'\btext-3xl\b(?!\s+(?:md|sm|lg):)', r'text-xl md:text-3xl', content)
    # text-2xl -> text-lg md:text-2xl
    content = re.sub(r'\btext-2xl\b(?!\s+(?:md|sm|lg):)', r'text-lg md:text-2xl', content)
    
    if 'text-' in original_content and 'md:text-' not in original_content:
        changes.append("text size'ları responsive yaptı")
    
    # 5. Padding/Margin mobilde küçült
    # p-8 -> p-4 md:p-8
    content = re.sub(r'\bp-8\b(?!\s+(?:md|sm|lg):)', r'p-4 md:p-8', content)
    # p-6 -> p-3 md:p-6
    content = re.sub(r'\bp-6\b(?!\s+(?:md|sm|lg):)', r'p-3 md:p-6', content)
    # px-8 -> px-4 md:px-8
    content = re.sub(r'\bpx-8\b(?!\s+(?:md|sm|lg):)', r'px-4 md:px-8', content)
    # py-8 -> py-4 md:py-8
    content = re.sub(r'\bpy-8\b(?!\s+(?:md|sm|lg):)', r'py-4 md:py-8', content)
    
    if ('p-8' in original_content or 'p-6' in original_content) and 'md:p-' not in original_content:
        changes.append("padding değerlerini responsive yaptı")
    
    # 6. Grid columns responsive yap
    # grid-cols-3 -> grid-cols-1 md:grid-cols-3
    content = re.sub(r'\bgrid-cols-3\b(?!\s+(?:md|sm|lg):)', r'grid-cols-1 md:grid-cols-2 lg:grid-cols-3', content)
    # grid-cols-4 -> grid-cols-1 md:grid-cols-4
    content = re.sub(r'\bgrid-cols-4\b(?!\s+(?:md|sm|lg):)', r'grid-cols-1 md:grid-cols-2 lg:grid-cols-4', content)
    # grid-cols-2 -> grid-cols-1 md:grid-cols-2
    content = re.sub(r'\bgrid-cols-2\b(?!\s+(?:md|sm|lg):)', r'grid-cols-1 md:grid-cols-2', content)
    
    if 'grid-cols-' in original_content and 'md:grid-cols-' not in original_content:
        changes.append("grid columns responsive yaptı")
    
    # 7. Flex direction - mobilde column
    if 'flex flex-row' in content and 'flex-col' not in content:
        content = re.sub(r'\bflex flex-row\b', r'flex flex-col md:flex-row', content)
        changes.append("flex direction responsive yaptı")
    
    # 8. Gap değerlerini mobilde küçült
    content = re.sub(r'\bgap-8\b(?!\s+(?:md|sm|lg):)', r'gap-4 md:gap-8', content)
    content = re.sub(r'\bgap-6\b(?!\s+(?:md|sm|lg):)', r'gap-3 md:gap-6', content)
    
    if ('gap-8' in original_content or 'gap-6' in original_content) and 'md:gap-' not in original_content:
        changes.append("gap değerlerini responsive yaptı")
    
    # 9. Hidden on mobile - büyük tablolar için
    if '<table' in content and 'overflow-x-auto' not in content:
        content = re.sub(r'(<div[^>]*>)(\s*<table)', r'\1\n<div class="overflow-x-auto">\2', content)
        # Closing div ekle
        content = re.sub(r'(</table>\s*)(</div>)', r'\1</div>\n\2', content, count=1)
        changes.append("tablolara horizontal scroll ekledi")
    
    # 10. Button size'ları mobilde optimize et
    # h-14 -> h-12 md:h-14
    content = re.sub(r'\bh-14\b(?!\s+(?:md|sm|lg):)', r'h-12 md:h-14', content)
    # h-16 -> h-14 md:h-16
    content = re.sub(r'\bh-16\b(?!\s+(?:md|sm|lg):)', r'h-14 md:h-16', content)
    
    # 11. Modal/Dialog genişlikleri
    if 'max-w-md' in content or 'max-w-lg' in content:
        content = re.sub(r'\bmax-w-md\b', r'max-w-full mx-4 sm:max-w-md', content)
        content = re.sub(r'\bmax-w-lg\b', r'max-w-full mx-4 sm:max-w-lg', content)
        content = re.sub(r'\bmax-w-xl\b', r'max-w-full mx-4 sm:max-w-xl', content)
        changes.append("modal genişliklerini mobil uyumlu yaptı")
    
    # 12. Overflow scroll for long content
    if 'whitespace-nowrap' in content and 'overflow-x-auto' not in content:
        content = re.sub(
            r'(class="[^"]*whitespace-nowrap[^"]*)"',
            r'\1 overflow-x-auto"',
            content
        )
        changes.append("whitespace-nowrap'a overflow ekledi")
    
    return content, changes

# Process all HTML files
for root, dirs, files in os.walk(templates_dir):
    for filename in files:
        if filename.endswith('.html'):
            filepath = os.path.join(root, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content, changes = fix_mobile_issues(content, filename)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    fixes_applied[filename] = changes
                    print(f"✅ {filename}:")
                    for change in changes:
                        print(f"   • {change}")
                else:
                    print(f"⏭️  {filename}: Mobil uyumlu")
            except Exception as e:
                print(f"❌ {filename}: Hata - {str(e)}")

print(f"\n{'='*70}")
print(f"📱 Mobil Uyumluluk Özeti:")
print(f"   ✅ {len(fixes_applied)} dosya güncellendi")
print(f"   ⏭️  {len([f for f in os.listdir(templates_dir) if f.endswith('.html')]) - len(fixes_applied)} dosya zaten uyumlu")
print(f"{'='*70}")

if fixes_applied:
    print(f"\n📋 Yapılan İyileştirmeler:")
    all_changes = {}
    for changes in fixes_applied.values():
        for change in changes:
            all_changes[change] = all_changes.get(change, 0) + 1
    
    for change, count in sorted(all_changes.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {change}: {count} dosya")
