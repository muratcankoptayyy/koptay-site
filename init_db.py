"""
Initialize database with test data
"""
from app import app, db
from models import User, TevkilPost, Application, Notification
from datetime import datetime, timezone, timedelta

def create_test_data():
    """Create test users and posts"""
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        print("✅ Database reset!")
        
        # Create test users
        user1 = User(
            email='ahmet@example.com',
            full_name='Ahmet Yılmaz',
            phone='0532 123 4567',
            whatsapp_number='0532 123 4567',
            bar_association='İstanbul Barosu',
            bar_registration_number='12345',
            city='İstanbul',
            district='Kadıköy',
            specializations=['Boşanma', 'Miras', 'Aile Hukuku'],
            bio='15 yıllık deneyimli avukat. Boşanma ve miras hukuku konularında uzmanım.',
            is_verified=True,
            is_active=True,
            rating_average=4.8,
            rating_count=45,
            total_posts_created=12,
            total_applications_sent=8,
            total_applications_received=34,
            accepted_applications=15,
            completed_jobs=12
        )
        user1.set_password('123456')
        
        user2 = User(
            email='ayse@example.com',
            full_name='Ayşe Demir',
            phone='0533 987 6543',
            whatsapp_number='0533 987 6543',
            bar_association='Ankara Barosu',
            bar_registration_number='67890',
            city='Ankara',
            district='Çankaya',
            specializations=['Ticaret Hukuku', 'İş Hukuku'],
            bio='Ticaret ve iş hukuku alanında 10 yıllık tecrübe.',
            is_verified=True,
            is_active=True,
            rating_average=4.6,
            rating_count=28,
            total_posts_created=8,
            total_applications_sent=15,
            total_applications_received=22,
            accepted_applications=10,
            completed_jobs=8
        )
        user2.set_password('123456')
        
        user3 = User(
            email='mehmet@example.com',
            full_name='Mehmet Kaya',
            phone='0534 555 1234',
            bar_association='İzmir Barosu',
            bar_registration_number='11223',
            city='İzmir',
            district='Konak',
            specializations=['Ceza Hukuku', 'İdare Hukuku'],
            bio='Ceza ve idare hukuku uzmanı.',
            is_verified=True,
            is_active=True,
            rating_average=4.5,
            rating_count=18
        )
        user3.set_password('123456')
        
        db.session.add_all([user1, user2, user3])
        db.session.commit()
        print(f"✅ Created 3 test users")
        print(f"   - {user1.email} / 123456")
        print(f"   - {user2.email} / 123456")
        print(f"   - {user3.email} / 123456")
        
        # Create test posts
        post1 = TevkilPost(
            user_id=user1.id,
            title='Boşanma Davası - Kadıköy Adliyesi',
            description='Anlaşmalı boşanma davası için yardım arıyorum. Kadıköy Adliyesi\'nde duruşma var.',
            category='bosanma',
            urgency_level='normal',
            city='İstanbul',
            district='Kadıköy',
            courthouse='Kadıköy Adliyesi',
            remote_allowed=False,
            price_min=3000,
            price_max=5000,
            court_date=datetime.now(timezone.utc) + timedelta(days=15),
            status='active',
            views=45,
            applications_count=7,
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        
        post2 = TevkilPost(
            user_id=user2.id,
            title='Ticari Dava - Ankara',
            description='Şirketler arası sözleşme ihlali davası. Online görüşme mümkün.',
            category='ticaret',
            urgency_level='urgent',
            city='Ankara',
            district='Çankaya',
            courthouse='Ankara Adliyesi',
            remote_allowed=True,
            price_min=8000,
            price_max=12000,
            deadline=datetime.now(timezone.utc) + timedelta(days=10),
            status='active',
            views=28,
            applications_count=4,
            expires_at=datetime.now(timezone.utc) + timedelta(days=20)
        )
        
        post3 = TevkilPost(
            user_id=user1.id,
            title='Miras İhtilafı Davası',
            description='Miras paylaşımı konusunda anlaşmazlık var. Acil çözüm gerekli.',
            category='miras',
            urgency_level='very_urgent',
            city='İstanbul',
            district='Bakırköy',
            courthouse='Bakırköy Adliyesi',
            remote_allowed=False,
            price_min=5000,
            price_max=8000,
            court_date=datetime.now(timezone.utc) + timedelta(days=7),
            status='active',
            views=62,
            applications_count=12,
            expires_at=datetime.now(timezone.utc) + timedelta(days=15)
        )
        
        db.session.add_all([post1, post2, post3])
        db.session.commit()
        print(f"✅ Created 3 test posts")
        
        # Create test applications
        app1 = Application(
            post_id=post1.id,
            applicant_id=user2.id,
            message='Boşanma hukuku konusunda deneyimliyim. Size yardımcı olabilirim.',
            proposed_price=4000,
            status='pending',
            created_at=datetime.now(timezone.utc) - timedelta(hours=2)
        )
        
        app2 = Application(
            post_id=post1.id,
            applicant_id=user3.id,
            message='Bu tür davalarda çok tecrübem var. İyi referanslarım mevcut.',
            proposed_price=4500,
            status='pending',
            created_at=datetime.now(timezone.utc) - timedelta(hours=5)
        )
        
        app3 = Application(
            post_id=post2.id,
            applicant_id=user1.id,
            message='Ticaret hukuku alanında uzmanım. Online görüşme yapabiliriz.',
            proposed_price=10000,
            status='accepted',
            created_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        
        db.session.add_all([app1, app2, app3])
        db.session.commit()
        print(f"✅ Created 3 test applications")
        
        # Create test notifications
        notif1 = Notification(
            user_id=user1.id,
            type='new_application',
            title='Yeni Başvuru',
            message='Ayşe Demir ilanınıza başvurdu',
            related_post_id=post1.id,
            related_user_id=user2.id,
            action_url='/applications',
            created_at=datetime.now(timezone.utc) - timedelta(hours=2)
        )
        
        notif2 = Notification(
            user_id=user1.id,
            type='new_application',
            title='Yeni Başvuru',
            message='Mehmet Kaya ilanınıza başvurdu',
            related_post_id=post1.id,
            related_user_id=user3.id,
            action_url='/applications',
            created_at=datetime.now(timezone.utc) - timedelta(hours=5)
        )
        
        notif3 = Notification(
            user_id=user1.id,
            type='application_accepted',
            title='Başvuru Kabul Edildi',
            message='Ayşe Demir başvurunuzu kabul etti',
            related_post_id=post2.id,
            related_user_id=user2.id,
            action_url='/applications',
            created_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        
        db.session.add_all([notif1, notif2, notif3])
        db.session.commit()
        print(f"✅ Created 3 test notifications")
        
        print("\n" + "="*60)
        print("✅ Test data created successfully!")
        print("="*60)
        print("\n📧 Login Credentials:")
        print("   Email: ahmet@example.com")
        print("   Password: 123456")
        print("\n🚀 Run: python app.py")
        print("🌐 Visit: http://localhost:5000/dashboard")

if __name__ == '__main__':
    create_test_data()
