"""
Test başvurusu oluştur
"""
from app import app, db, TevkilPost, Application, User

with app.app_context():
    # İlk ilan
    post = TevkilPost.query.first()
    
    # İlk iki kullanıcı (farklı olmalı)
    user1 = User.query.first()
    user2 = User.query.offset(1).first()
    
    # Eğer ilan user2'ye aitse, user1'i başvuran yap
    if post.user_id == user2.id:
        applicant = user1
    else:
        applicant = user2
    
    # Başvuru oluştur
    application = Application(
        post_id=post.id,
        applicant_id=applicant.id,
        message="Test başvurusu - yetki belgesi testi için",
        proposed_price=5000,
        status='accepted'
    )
    
    db.session.add(application)
    db.session.commit()
    
    print(f"✅ Başvuru oluşturuldu!")
    print(f"   İlan: {post.title}")
    print(f"   İlan Sahibi: {post.user.full_name}")
    print(f"   Başvuran: {applicant.full_name}")
    print(f"   Durum: accepted")
