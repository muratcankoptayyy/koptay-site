
import os
from datetime import datetime, timedelta
import random
from app import app
from models import db, User, TevkilPost, Application, Conversation, Message, Notification

def create_test_data():
    with app.app_context():
        print("🚀 Test verileri oluşturuluyor...")

        # 1. Test Kullanıcıları Oluştur
        users = []
        cities = ['İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya']
        names = ['Ahmet Yılmaz', 'Ayşe Demir', 'Mehmet Kaya', 'Fatma Çelik', 'Ali Öztürk']
        
        for i, name in enumerate(names):
            email = f"user{i+1}@example.com"
            user = User.query.filter_by(email=email).first()
            
            if not user:
                user = User(
                    email=email,
                    full_name=name,
                    phone=f"555{random.randint(1000000, 9999999)}",
                    city=random.choice(cities),
                    lawyer_type='lawyer',
                    is_verified=True
                )
                user.set_password('password123')
                user.generate_api_token()
                db.session.add(user)
                print(f"✅ Kullanıcı oluşturuldu: {name} ({email})")
            else:
                print(f"ℹ️ Kullanıcı zaten var: {name}")
            
            users.append(user)
        
        db.session.commit()

        # Mevcut kullanıcıyı bul (Login olan kullanıcı)
        # Genellikle ilk kullanıcı veya admin olabilir, ama biz user1'i baz alalım
        # veya veritabanındaki ilk kullanıcıyı alalım
        current_user = User.query.first()
        if not current_user:
            print("❌ Hiç kullanıcı bulunamadı!")
            return

        print(f"👤 Aktif kullanıcı varsayılıyor: {current_user.full_name}")

        # 2. İlanlar Oluştur (Diğer kullanıcılar tarafından)
        categories = ['Duruşma', 'Haciz', 'Dosya İnceleme', 'Satış Memurluğu', 'Tapu İşlemleri']
        
        for _ in range(10):
            owner = random.choice([u for u in users if u.id != current_user.id])
            
            post = TevkilPost(
                user_id=owner.id,
                title=f"{random.choice(cities)} {random.choice(categories)} İşi",
                description="Bu bir test ilanıdır. Detaylar konuşulacaktır. Lütfen sadece tecrübeli meslektaşlar başvursun.",
                category=random.choice(categories),
                city=owner.city,
                district="Merkez",
                courthouse=f"{owner.city} Adliyesi",
                urgency_level=random.choice(['normal', 'urgent', 'high']),
                price_min=random.randint(1000, 3000),
                price_max=random.randint(3000, 5000),
                deadline=datetime.now() + timedelta(days=random.randint(1, 7)),
                court_date=datetime.now() + timedelta(days=random.randint(2, 10))
            )
            db.session.add(post)
        
        print("✅ 10 adet test ilanı oluşturuldu")
        db.session.commit()

        # 3. Başvurular Oluştur
        # Aktif kullanıcı başkalarının ilanına başvursun
        other_posts = TevkilPost.query.filter(TevkilPost.user_id != current_user.id).limit(3).all()
        for post in other_posts:
            if not Application.query.filter_by(post_id=post.id, applicant_id=current_user.id).first():
                application = Application(
                    post_id=post.id,
                    applicant_id=current_user.id,
                    message="Merhaba, bu iş için uygunum. Yardımcı olabilirim.",
                    proposed_price=post.price_min
                )
                db.session.add(application)
                post.applications_count += 1
                current_user.total_applications_sent += 1
        
        print("✅ Aktif kullanıcı adına 3 başvuru yapıldı")

        # Başkaları aktif kullanıcının ilanına başvursun (Eğer ilanı varsa)
        my_posts = TevkilPost.query.filter_by(user_id=current_user.id).all()
        if not my_posts:
            # İlan yoksa bir tane oluşturalım
            my_post = TevkilPost(
                user_id=current_user.id,
                title="Acil Duruşma Tevkili",
                description="Kendi ilanım. Test amaçlı.",
                category="Duruşma",
                city=current_user.city,
                urgency_level="urgent",
                price_min=2000,
                price_max=4000,
                deadline=datetime.now() + timedelta(days=3),
                court_date=datetime.now() + timedelta(days=5)
            )
            db.session.add(my_post)
            db.session.commit()
            my_posts = [my_post]
            print("✅ Aktif kullanıcı için test ilanı oluşturuldu")

        for post in my_posts:
            applicant = random.choice([u for u in users if u.id != current_user.id])
            if not Application.query.filter_by(post_id=post.id, applicant_id=applicant.id).first():
                application = Application(
                    post_id=post.id,
                    applicant_id=applicant.id,
                    message="Müsaitim, ilgileniyorum.",
                    proposed_price=post.price_min
                )
                db.session.add(application)
                post.applications_count += 1
        
        print("✅ Aktif kullanıcının ilanlarına başvurular eklendi")
        db.session.commit()

        # 4. Mesajlaşma Oluştur
        other_user = [u for u in users if u.id != current_user.id][0]
        
        # Konuşma var mı?
        conv = Conversation.query.filter(
            ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == other_user.id)) |
            ((Conversation.user1_id == other_user.id) & (Conversation.user2_id == current_user.id))
        ).first()
        
        if not conv:
            conv = Conversation(
                user1_id=current_user.id,
                user2_id=other_user.id,
                post_id=other_posts[0].id if other_posts else None
            )
            db.session.add(conv)
            db.session.commit()
        
        # Mesajlar
        msgs = [
            (other_user.id, "Merhaba, ilanınızla ilgileniyorum."),
            (current_user.id, "Merhaba, tabii buyurun."),
            (other_user.id, "Dosya detaylarını öğrenebilir miyim?"),
            (current_user.id, "Tabii, dosya numarası 2025/123."),
        ]
        
        for sender_id, text in msgs:
            msg = Message(
                conversation_id=conv.id,
                sender_id=sender_id,
                message=text
            )
            db.session.add(msg)
            
            conv.last_message_at = datetime.now(timezone.utc)
            conv.last_message_text = text
            conv.last_message_sender_id = sender_id
            
            if sender_id != current_user.id:
                conv.unread_count_user1 += 1 # Varsayalım user1 biziz
            
        print("✅ Test mesajlaşması oluşturuldu")
        
        # 5. Bildirimler
        notif = Notification(
            user_id=current_user.id,
            type='system',
            title='Hoşgeldiniz',
            message='UTAP mobil uygulamasına hoşgeldiniz! Profilinizi tamamlamayı unutmayın.',
            action_url='/profile'
        )
        db.session.add(notif)
        print("✅ Test bildirimi oluşturuldu")
        
        db.session.commit()
        print("✨ Tüm test verileri başarıyla oluşturuldu!")

if __name__ == '__main__':
    from datetime import timezone
    create_test_data()
