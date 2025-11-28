#!/bin/bash
# PythonAnywhere Deployment Script
# Kullanıcı: muratcankoptay
# Proje: Ulusal Tevkil Ağı Projesi - Phoenix Theme Update

echo "🚀 Ulusal Tevkil Ağı - PythonAnywhere Deploy (Phoenix Theme)"
echo "Kullanıcı: muratcankoptay"
echo "=========================================="
echo ""

# Proje dizinine git
cd /home/muratcankoptay/tevkil_proje

# Git güncellemesi yap
echo "📥 Son değişiklikler çekiliyor..."
git pull origin main

# Virtual environment oluştur (yoksa)
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment oluşturuluyor..."
    python3.11 -m venv venv
fi

source venv/bin/activate

# Bağımlılıkları yükle
echo "📥 Bağımlılıklar güncelleniyor..."
pip install --upgrade pip
pip install -r requirements.txt

# Phoenix theme CSS'ini build et
echo "🎨 Phoenix Theme CSS build ediliyor..."
cd themes/phoenix
npx tailwindcss -i ./src/styles/input.css -o ./static/css/main.css --minify
cp static/css/main.css ../../static/phoenix/css/main.css
cd ../..

# Database migration (varsa)
echo "�️  Database kontrol ediliyor..."
python3.11 << END
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Database hazır!")
END

echo ""
echo "✅ Deployment tamamlandı!"
echo ""
echo "📋 ŞİMDİ YAPMANIZ GEREKENLER:"
echo "1. PythonAnywhere Web sekmesine gidin"
echo "2. 'Reload muratcankoptay.pythonanywhere.com' butonuna basın"
echo "3. https://muratcankoptay.pythonanywhere.com adresini açın"
echo ""
echo "🎨 Phoenix Theme ile yeni görünüm aktif olacak!"
echo ""
