"""
HTML dosyalarındaki encoding sorunlarını düzelt
"""
import os
import glob

def fix_html_files():
    template_files = glob.glob('templates/*.html')
    
    for file_path in template_files:
        try:
            # Dosyayı oku (farklı encoding'lerle dene)
            content = None
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except:
                    continue
            
            if content:
                # Bozuk karakterleri düzelt
                content = content.replace('Ulusal Tevkil A�� Projesi', 'utap')
                content = content.replace('�', '')
                
                # UTF-8 ile yeniden yaz
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ {file_path} düzeltildi")
        except Exception as e:
            print(f"❌ {file_path} hatası: {e}")

if __name__ == "__main__":
    fix_html_files()
    print("\n✨ Tüm dosyalar düzeltildi!")
