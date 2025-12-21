
import os

file_path = 'blueprints/api/routes.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove emojis
content = content.replace('❌ ', '')
content = content.replace('🔑 ', '')
content = content.replace('⚠️ ', '')
content = content.replace('✅ ', '')
content = content.replace('📡 ', '')
content = content.replace('🔓 ', '')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Cleaned emojis from routes.py")
