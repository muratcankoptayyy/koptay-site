#!/usr/bin/env python3
"""
Minimal White Tema - Toplu Değişiklik Script
Tüm template dosyalarında eski stil class'ları minimal white tema stillerine çevirir
"""

import os
import re
from pathlib import Path

# Değişiklik kuralları
REPLACEMENTS = [
    # Rounded corners → keskin köşeler
    (r'\brounded-lg\b', ''),
    (r'\brounded-md\b', ''),
    (r'\brounded-xl\b', ''),
    (r'\brounded\b(?!-full)', ''),  # rounded-full hariç (avatarlar için)
    
    # Shadows → flat design
    (r'\bshadow-lg\b', ''),
    (r'\bshadow-md\b', ''),
    (r'\bshadow-sm\b', ''),
    (r'\bshadow-xl\b', ''),
    (r'\bhover:shadow-\w+\b', ''),
    
    # Border colors → border-gray-300
    (r'\bborder-gray-100\b', 'border-gray-300'),
    (r'\bborder-gray-200\b(?!-)', 'border-gray-300'),  # border-gray-200 ancak başka bir şey takip etmiyorsa
    
    # Background colors
    (r'\bbg-blue-500\b', 'bg-gray-900'),
    (r'\bbg-blue-600\b', 'bg-gray-900'),
    (r'\bbg-blue-700\b', 'bg-gray-900'),
    (r'\bbg-primary\b', 'bg-gray-900'),
    
    # Text colors
    (r'\btext-blue-500\b', 'text-gray-900'),
    (r'\btext-blue-600\b', 'text-gray-900'),
    (r'\btext-primary\b(?!-)', 'text-gray-900'),
    
    # Font weights → light/medium
    (r'\bfont-black\b', 'font-light'),
    (r'\bfont-extrabold\b', 'font-medium'),
    
    # Hover effects
    (r'\bhover:bg-blue-\d+\b', 'hover:bg-gray-800'),
    (r'\bhover:bg-primary\b', 'hover:bg-gray-800'),
    (r'\bhover:text-primary\b', 'hover:text-gray-900'),
    
    # Gradient backgrounds → solid white
    (r'\bbg-gradient-to-\w+\b\s+from-\S+\s+to-\S+', 'bg-white'),
]

def clean_classes(html_content):
    """HTML içindeki class attribute'larını temizle"""
    
    def replace_class_attr(match):
        classes = match.group(1)
        
        # Her replacement kuralını uygula
        for pattern, replacement in REPLACEMENTS:
            classes = re.sub(pattern, replacement, classes)
        
        # Çift boşlukları temizle
        classes = re.sub(r'\s+', ' ', classes).strip()
        
        # Boş class attribute'u kaldır
        if not classes:
            return ''
        
        return f'class="{classes}"'
    
    # class="..." pattern'lerini bul ve değiştir
    html_content = re.sub(r'class="([^"]*)"', replace_class_attr, html_content)
    
    return html_content

def process_file(file_path):
    """Bir HTML dosyasını işle"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Değişiklik yap
        new_content = clean_classes(content)
        
        # Değişiklik oldu mu kontrol et
        if content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Hata: {file_path} - {e}")
        return False

def main():
    """Ana fonksiyon"""
    templates_dir = Path('templates')
    
    if not templates_dir.exists():
        print("❌ templates klasörü bulunamadı!")
        return
    
    # Tüm HTML dosyalarını bul
    html_files = list(templates_dir.glob('**/*.html'))
    
    print(f"📁 {len(html_files)} HTML dosyası bulundu\n")
    
    processed = 0
    changed = 0
    
    for html_file in html_files:
        if process_file(html_file):
            changed += 1
            print(f"✅ Güncellendi: {html_file.name}")
        else:
            print(f"⏭️  Değişiklik yok: {html_file.name}")
        processed += 1
    
    print(f"\n{'='*60}")
    print(f"✨ Tamamlandı!")
    print(f"📊 {processed} dosya işlendi")
    print(f"🔄 {changed} dosya güncellendi")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
