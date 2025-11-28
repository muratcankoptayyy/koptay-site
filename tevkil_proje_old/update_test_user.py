"""
Test kullanıcılarına gerçekçi veriler ekle
"""
from app import app, db, User

with app.app_context():
    # İlk kullanıcıyı güncelle
    user1 = User.query.first()
    if user1:
        user1.bar_association = "Ankara Barosu"
        user1.bar_registration_number = "12345"
        user1.address = "Çankaya/Ankara Kızılay Mahallesi Atatürk Bulvarı No:10 Kat:3"
        user1.tc_number = "12345678901"
        print(f"✅ {user1.full_name} güncellendi")
        print(f"   Baro: {user1.bar_association}")
        print(f"   Sicil: {user1.bar_registration_number}")
        print(f"   Adres: {user1.address}")
    
    # İkinci kullanıcıyı güncelle
    user2 = User.query.offset(1).first()
    if user2:
        user2.bar_association = "İstanbul Barosu"
        user2.bar_registration_number = "67890"
        user2.address = "Kadıköy/İstanbul Bağdat Caddesi No:150 Daire:5"
        user2.tc_number = "98765432109"
        print(f"✅ {user2.full_name} güncellendi")
        print(f"   Baro: {user2.bar_association}")
        print(f"   Sicil: {user2.bar_registration_number}")
        print(f"   Adres: {user2.address}")
    
    # Üçüncü kullanıcıyı güncelle
    user3 = User.query.offset(2).first()
    if user3:
        user3.bar_association = "İzmir Barosu"
        user3.bar_registration_number = "11111"
        user3.address = "Konak/İzmir Cumhuriyet Bulvarı No:25"
        user3.tc_number = "11122233344"
        print(f"✅ {user3.full_name} güncellendi")
        print(f"   Baro: {user3.bar_association}")
        print(f"   Sicil: {user3.bar_registration_number}")
        print(f"   Adres: {user3.address}")
    
    db.session.commit()
    print("\n🎉 Tüm kullanıcılar güncellendi!")
