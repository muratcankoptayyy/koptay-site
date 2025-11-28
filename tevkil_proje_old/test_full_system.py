"""
Komple WhatsApp Bot Testi
1. Kullanıcı oluştur/güncelle
2. WhatsApp numarası ekle
3. İlan oluştur
4. Bildirim gönder
"""
import os
os.environ['FLASK_ENV'] = 'development'

from app import app, db
from models import User, TevkilPost
from whatsapp_bot import WhatsAppBot
from datetime import datetime, timezone, timedelta

def full_system_test():
    """Tam sistem testi"""
    
    print("=" * 60)
    print("TEVKIL AĞI - WHATSAPP BOT TAM SİSTEM TESTİ")
    print("=" * 60)
    
    with app.app_context():
        # 1. Test kullanıcısı bul veya oluştur
        print("\n1️⃣ KULLANICI KONTROLÜ:")
        user = User.query.filter_by(email='ahmet.yilmaz@example.com').first()
        
        if user:
            print(f"✅ Kullanıcı bulundu: {user.full_name}")
            print(f"📱 Mevcut WhatsApp: {user.whatsapp_number or 'Kayıtlı değil'}")
            
            # WhatsApp numarasını güncelle
            if not user.whatsapp_number or user.whatsapp_number != '905307111864':
                user.whatsapp_number = '905307111864'
                db.session.commit()
                print(f"✅ WhatsApp numarası güncellendi: {user.whatsapp_number}")
        else:
            print("❌ Test kullanıcısı bulunamadı!")
            print("Lütfen siteye giriş yapın: http://localhost:5000/login")
            print("Email: ahmet.yilmaz@example.com")
            print("Password: 123456")
            return
        
        # 2. Test mesajı ile ilan oluştur
        print("\n2️⃣ İLAN OLUŞTURMA TESTİ:")
        
        test_message = """#ILAN
Başlık: Test - İstanbul Anadolu Adliyesi Duruşma
Kategori: Ceza Hukuku
Şehir: İstanbul
Açıklama: Bu bir test ilanıdır. Meta WhatsApp API test ediliyor.
Fiyat: 2500
Aciliyet: Acil"""
        
        print(f"Test Mesajı:\n{test_message}\n")
        
        bot = WhatsAppBot()
        success, response = bot.create_post_from_whatsapp('905307111864', test_message)
        
        if success:
            print(f"✅ {response}")
            
            # En son oluşturulan ilanı bul
            latest_post = TevkilPost.query.order_by(TevkilPost.created_at.desc()).first()
            if latest_post:
                print(f"\n📋 Oluşturulan İlan:")
                print(f"  ID: {latest_post.id}")
                print(f"  Başlık: {latest_post.title}")
                print(f"  Kategori: {latest_post.category}")
                print(f"  Şehir: {latest_post.location}")
                print(f"  Fiyat: {latest_post.price_max} TL")
                print(f"  Durum: {latest_post.status}")
                print(f"  Link: http://localhost:5000/posts/{latest_post.id}")
        else:
            print(f"❌ {response}")
            return
        
        # 3. Bildirim testi
        print("\n3️⃣ WHATSAPP BİLDİRİM TESTİ:")
        
        from whatsapp_meta_api import send_post_created_confirmation
        
        try:
            send_post_created_confirmation(
                post_title=latest_post.title,
                post_id=latest_post.id,
                recipient_phone='905307111864'
            )
            print("✅ İlan oluşturma bildirimi gönderildi!")
            print("📱 WhatsApp'ını kontrol et!")
        except Exception as e:
            print(f"❌ Bildirim gönderilemedi: {str(e)}")
        
        print("\n" + "=" * 60)
        print("TEST TAMAMLANDI!")
        print("=" * 60)
        print("\nYapılacaklar:")
        print("1. WhatsApp'ı kontrol et (bildirim geldi mi?)")
        print("2. Web sitesini aç: http://localhost:5000/posts")
        print("3. İlanı gör ve test et!")
        print("\nBaşvuru testi için:")
        print("- Başka bir hesapla giriş yap")
        print("- Bu ilana başvur")
        print("- İlan sahibine (senin numaraya) bildirim gelecek!")

if __name__ == "__main__":
    full_system_test()
