"""
📊 İstatistik sistemi için database migration
Yeni kolonlar ve hesaplamalar
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app as flask_app, db
from models import User, TevkilPost, Application, Rating
from sqlalchemy import text
from datetime import datetime, timedelta

def upgrade_statistics():
    """İstatistik alanlarını ekle ve mevcut verileri hesapla"""
    
    with flask_app.app_context():
        print("📊 İstatistik sistemi migration başlatılıyor...")
        
        # 1. User tablosuna yeni istatistik kolonları ekle
        print("\n👤 User tablosuna istatistik kolonları ekleniyor...")
        
        new_user_columns = [
            ("total_posts_created", "INTEGER DEFAULT 0", "Oluşturulan toplam ilan"),
            ("total_applications_sent", "INTEGER DEFAULT 0", "Gönderilen toplam başvuru"),
            ("total_applications_received", "INTEGER DEFAULT 0", "Alınan toplam başvuru"),
            ("accepted_applications", "INTEGER DEFAULT 0", "Kabul edilen başvurular"),
            ("rejected_applications", "INTEGER DEFAULT 0", "Reddedilen başvurular"),
            ("average_response_time_hours", "FLOAT DEFAULT 0.0", "Ortalama yanıt süresi (saat)"),
            ("total_views_received", "INTEGER DEFAULT 0", "İlanların toplam görüntülenmesi"),
            ("profile_views", "INTEGER DEFAULT 0", "Profil görüntülenmesi"),
            ("last_post_date", "DATETIME", "Son ilan tarihi"),
            ("last_application_date", "DATETIME", "Son başvuru tarihi"),
        ]
        
        for col_name, col_type, desc in new_user_columns:
            try:
                db.session.execute(text(f"""
                    ALTER TABLE users ADD COLUMN {col_name} {col_type}
                """))
                db.session.commit()
                print(f"   ✅ {desc} ({col_name}) eklendi")
            except Exception as e:
                if "duplicate column" not in str(e).lower():
                    print(f"   ⚠️  {col_name}: {e}")
                db.session.rollback()
        
        # 2. TevkilPost tablosuna ek istatistik kolonları
        print("\n📄 TevkilPost tablosuna istatistik kolonları ekleniyor...")
        
        new_post_columns = [
            ("view_count", "INTEGER DEFAULT 0", "Görüntülenme sayısı"),
            ("unique_viewers", "INTEGER DEFAULT 0", "Benzersiz görüntüleyici"),
            ("application_rate", "FLOAT DEFAULT 0.0", "Başvuru oranı (%)"),
            ("average_application_response", "FLOAT DEFAULT 0.0", "Ort. başvuru yanıt süresi"),
            ("last_viewed_at", "DATETIME", "Son görüntülenme zamanı"),
            ("first_application_at", "DATETIME", "İlk başvuru zamanı"),
        ]
        
        for col_name, col_type, desc in new_post_columns:
            try:
                db.session.execute(text(f"""
                    ALTER TABLE tevkil_posts ADD COLUMN {col_name} {col_type}
                """))
                db.session.commit()
                print(f"   ✅ {desc} ({col_name}) eklendi")
            except Exception as e:
                if "duplicate column" not in str(e).lower():
                    print(f"   ⚠️  {col_name}: {e}")
                db.session.rollback()
        
        # 3. Mevcut verileri hesapla ve güncelle
        print("\n🔄 Mevcut veriler hesaplanıyor...")
        
        all_users = User.query.all()
        
        for user in all_users:
            # İlan istatistikleri
            user_posts = TevkilPost.query.filter_by(user_id=user.id).all()
            user.total_posts_created = len(user_posts)
            
            if user_posts:
                user.last_post_date = max(post.created_at for post in user_posts)
                user.total_views_received = sum(post.views or 0 for post in user_posts)
            
            # Başvuru istatistikleri (gönderilen)
            sent_applications = Application.query.filter_by(applicant_id=user.id).all()
            user.total_applications_sent = len(sent_applications)
            
            if sent_applications:
                user.last_application_date = max(app.created_at for app in sent_applications)
            
            # Başvuru istatistikleri (alınan)
            user_post_ids = [post.id for post in user_posts]
            received_applications = Application.query.filter(
                Application.post_id.in_(user_post_ids)
            ).all() if user_post_ids else []
            
            user.total_applications_received = len(received_applications)
            
            # Kabul/Red sayıları
            user.accepted_applications = len([app for app in received_applications if app.status == 'accepted'])
            user.rejected_applications = len([app for app in received_applications if app.status == 'rejected'])
            
            # Yanıt süresi hesapla
            if received_applications:
                response_times = []
                for app in received_applications:
                    # Status değişikliği varsa updated_at'ı kullan
                    if app.status in ['accepted', 'rejected'] and app.updated_at:
                        diff = (app.updated_at - app.created_at).total_seconds() / 3600
                        response_times.append(diff)
                
                if response_times:
                    user.average_response_time_hours = sum(response_times) / len(response_times)
            
            # Başarı oranı
            total_reviews = user.accepted_applications + user.rejected_applications
            if total_reviews > 0:
                user.success_rate = (user.accepted_applications / total_reviews) * 100
        
        # Her ilan için başvuru oranını hesapla
        all_posts = TevkilPost.query.all()
        
        for post in all_posts:
            # view_count'u views'dan kopyala (eski alan varsa)
            if hasattr(post, 'views') and post.views:
                post.view_count = post.views
            
            # Başvuru sayısı
            post_applications = Application.query.filter_by(post_id=post.id).all()
            post.applications_count = len(post_applications)
            
            # Başvuru oranı (view varsa)
            if post.view_count and post.view_count > 0:
                post.application_rate = (post.applications_count / post.view_count) * 100
            
            # İlk başvuru zamanı
            if post_applications:
                post.first_application_at = min(app.created_at for app in post_applications)
        
        db.session.commit()
        
        # 4. İstatistikler
        print("\n" + "="*60)
        print("✨ İstatistik sistemi migration tamamlandı!")
        print("="*60)
        print(f"👤 Toplam kullanıcı: {User.query.count()}")
        print(f"📄 Toplam ilan: {TevkilPost.query.count()}")
        print(f"📬 Toplam başvuru: {Application.query.count()}")
        print(f"⭐ Toplam değerlendirme: {Rating.query.count()}")
        
        # En aktif kullanıcılar
        top_creators = User.query.order_by(User.total_posts_created.desc()).limit(5).all()
        print("\n🏆 En çok ilan oluşturan kullanıcılar:")
        for i, user in enumerate(top_creators, 1):
            print(f"   {i}. {user.full_name}: {user.total_posts_created} ilan")
        
        # En çok görüntülenen ilanlar
        top_posts = TevkilPost.query.order_by(TevkilPost.view_count.desc()).limit(5).all()
        print("\n👁️  En çok görüntülenen ilanlar:")
        for i, post in enumerate(top_posts, 1):
            print(f"   {i}. {post.title[:40]}: {post.view_count} görüntüleme")
        
        print("\n💡 Öneriler:")
        print("   - Flask uygulamasını yeniden başlatın")
        print("   - Dashboard'da yeni istatistikleri görüntüleyin")
        print("   - /stats sayfasını kontrol edin")
        print("="*60)

if __name__ == '__main__':
    upgrade_statistics()
