#!/bin/bash
# PythonAnywhere Quick Deploy Script
# Bu dosyayı PythonAnywhere Bash console'da çalıştırın

echo "🚀 Ulusal Tevkil Ağı - PythonAnywhere Deploy"
echo "=========================================="

# 1. Virtual environment oluştur
echo "📦 Virtual environment oluşturuluyor..."
python3.11 -m venv venv
source venv/bin/activate

# 2. Bağımlılıkları yükle
echo "📥 Bağımlılıklar yükleniyor..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Database oluştur
echo "🗄️  Database oluşturuluyor..."
python << END
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Database oluşturuldu!")
END

# 4. Test kullanıcısı ekle (isteğe bağlı)
echo "👤 Test kullanıcısı eklemek ister misiniz? (y/n)"
read -r answer
if [ "$answer" = "y" ]; then
    python << END
from app import app, db, User
with app.app_context():
    user = User(
        email='admin@tevkil.com',
        full_name='Admin User',
        city='İstanbul',
        bar_association='İstanbul Barosu',
        lawyer_type='avukat'
    )
    user.set_password('admin123')
    db.session.add(user)
    db.session.commit()
    print("✅ Test kullanıcısı oluşturuldu!")
    print("Email: admin@tevkil.com")
    print("Şifre: admin123")
END
fi

echo ""
echo "✅ Deploy tamamlandı!"
echo ""
echo "📋 Şimdi yapmanız gerekenler:"
echo "1. PythonAnywhere Web sekmesine gidin"
echo "2. 'Reload' butonuna basın"
echo "3. Sitenizi ziyaret edin!"
echo ""
