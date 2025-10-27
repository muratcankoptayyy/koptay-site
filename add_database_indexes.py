"""
Veritabanı Optimizasyonu Migration
- Index ekleme
- Performance iyileştirmeleri
"""
from models import db
from sqlalchemy import text

def add_database_indexes():
    """Performans için indexler ekle"""
    
    indexes = [
        # TevkilPost için indexler
        "CREATE INDEX IF NOT EXISTS idx_tevkil_posts_city ON tevkil_posts(city)",
        "CREATE INDEX IF NOT EXISTS idx_tevkil_posts_category ON tevkil_posts(category)",
        "CREATE INDEX IF NOT EXISTS idx_tevkil_posts_created_at ON tevkil_posts(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_tevkil_posts_urgency ON tevkil_posts(urgency_level)",
        "CREATE INDEX IF NOT EXISTS idx_tevkil_posts_status ON tevkil_posts(status)",
        "CREATE INDEX IF NOT EXISTS idx_tevkil_posts_user_id ON tevkil_posts(user_id)",
        
        # Application için indexler
        "CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status)",
        "CREATE INDEX IF NOT EXISTS idx_applications_post_id ON applications(post_id)",
        "CREATE INDEX IF NOT EXISTS idx_applications_applicant_id ON applications(applicant_id)",
        "CREATE INDEX IF NOT EXISTS idx_applications_created_at ON applications(created_at DESC)",
        
        # Message için indexler  
        "CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id)",
        "CREATE INDEX IF NOT EXISTS idx_messages_receiver_id ON messages(receiver_id)",
        "CREATE INDEX IF NOT EXISTS idx_messages_sent_at ON messages(sent_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_messages_read ON messages(is_read)",
        
        # Notification için indexler
        "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read)",
        "CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC)",
        
        # Rating için indexler
        "CREATE INDEX IF NOT EXISTS idx_ratings_reviewed_id ON ratings(reviewed_id)",
        "CREATE INDEX IF NOT EXISTS idx_ratings_reviewer_id ON ratings(reviewer_id)",
        "CREATE INDEX IF NOT EXISTS idx_ratings_created_at ON ratings(created_at DESC)",
        
        # Favorite için indexler
        "CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_favorites_post_id ON favorites(post_id)",
        
        # Report için indexler
        "CREATE INDEX IF NOT EXISTS idx_reports_reporter_id ON reports(reporter_id)",
        "CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)",
        "CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at DESC)",
        
        # Composite indexler (sık birlikte kullanılanlar)
        "CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(sender_id, receiver_id, sent_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_tevkil_posts_active ON tevkil_posts(status, created_at DESC) WHERE status = 'active'",
        "CREATE INDEX IF NOT EXISTS idx_applications_pending ON applications(post_id, status) WHERE status = 'pending'",
    ]
    
    print("📊 Veritabanı indexleri oluşturuluyor...")
    
    for index_sql in indexes:
        try:
            db.session.execute(text(index_sql))
            print(f"✅ {index_sql[:60]}...")
        except Exception as e:
            print(f"⚠️ Index hatası: {str(e)[:100]}")
    
    try:
        db.session.commit()
        print("✅ Tüm indexler başarıyla oluşturuldu!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Index commit hatası: {e}")

if __name__ == '__main__':
    from app import app
    with app.app_context():
        add_database_indexes()
