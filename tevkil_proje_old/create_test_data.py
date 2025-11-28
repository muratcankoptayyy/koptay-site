"""
Test verileri oluştur - Demo kullanıcılar ve ilanlar
"""
from app import app, db
from models import User, TevkilPost, Application, Rating
from datetime import datetime, timedelta, timezone
import random

def create_test_data():
    with app.app_context():
        print("🚀 Test verileri oluşturuluyor...")
        
        # Mevcut verileri temizle (isteğe bağlı)
        # db.drop_all()
        # db.create_all()
        
        # 1. Test Kullanıcıları Oluştur
        test_users = [
            {
                'full_name': 'Ahmet Yılmaz',
                'email': 'ahmet.yilmaz@example.com',
                'phone': '0532 123 45 67',
                'city': 'İstanbul',
                'district': 'Kadıköy',
                'specializations': ['Ceza Hukuku', 'İcra İflas Hukuku'],
                'bio': '15 yıllık deneyime sahip ceza avukatıyım. İstanbul Barosu üyesiyim.'
            },
            {
                'full_name': 'Ayşe Demir',
                'email': 'ayse.demir@example.com',
                'phone': '0533 234 56 78',
                'city': 'Ankara',
                'district': 'Çankaya',
                'specializations': ['Aile Hukuku', 'Miras Hukuku'],
                'bio': '10 yıldır aile hukuku alanında çalışıyorum. Boşanma ve velayet davalarında uzmanım.'
            },
            {
                'full_name': 'Mehmet Kaya',
                'email': 'mehmet.kaya@example.com',
                'phone': '0534 345 67 89',
                'city': 'İzmir',
                'district': 'Konak',
                'specializations': ['İş Hukuku', 'Ticaret Hukuku'],
                'bio': 'İş hukuku ve ticaret hukuku alanında 8 yıllık tecrübem var.'
            },
            {
                'full_name': 'Fatma Şahin',
                'email': 'fatma.sahin@example.com',
                'phone': '0535 456 78 90',
                'city': 'Bursa',
                'district': 'Osmangazi',
                'specializations': ['İdare Hukuku', 'Vergi Hukuku'],
                'bio': 'İdare ve vergi hukuku alanında 12 yıllık deneyimim bulunmaktadır.'
            },
            {
                'full_name': 'Ali Öztürk',
                'email': 'ali.ozturk@example.com',
                'phone': '0536 567 89 01',
                'city': 'Antalya',
                'district': 'Muratpaşa',
                'specializations': ['Gayrimenkul Hukuku', 'İnşaat Hukuku'],
                'bio': 'Gayrimenkul ve inşaat hukuku uzmanıyım. Tapu iptali davalarında deneyimliyim.'
            },
            {
                'full_name': 'Zeynep Arslan',
                'email': 'zeynep.arslan@example.com',
                'phone': '0537 678 90 12',
                'city': 'İstanbul',
                'district': 'Beşiktaş',
                'specializations': ['Ceza Hukuku', 'Bilişim Hukuku'],
                'bio': 'Bilişim suçları ve siber güvenlik alanında uzmanım.'
            },
            {
                'full_name': 'Mustafa Çelik',
                'email': 'mustafa.celik@example.com',
                'phone': '0538 789 01 23',
                'city': 'Ankara',
                'district': 'Keçiören',
                'specializations': ['Sağlık Hukuku', 'Tıbbi Malpraktis'],
                'bio': 'Sağlık hukuku ve tıbbi malpraktis davalarında 6 yıllık deneyimim var.'
            },
            {
                'full_name': 'Elif Aydın',
                'email': 'elif.aydin@example.com',
                'phone': '0539 890 12 34',
                'city': 'İzmir',
                'district': 'Bornova',
                'specializations': ['Aile Hukuku', 'Çocuk Hakları'],
                'bio': 'Aile hukuku ve çocuk hakları alanında çalışmaktayım.'
            }
        ]
        
        users = []
        for user_data in test_users:
            user = User.query.filter_by(email=user_data['email']).first()
            if not user:
                user = User(
                    email=user_data['email'],
                    full_name=user_data['full_name'],
                    phone=user_data['phone'],
                    city=user_data['city'],
                    district=user_data.get('district'),
                    specializations=user_data['specializations'],
                    bio=user_data.get('bio'),
                    completed_jobs=random.randint(5, 50),
                    rating_average=round(random.uniform(4.0, 5.0), 1),
                    rating_count=random.randint(3, 30)
                )
                user.set_password('123456')  # Test şifresi
                db.session.add(user)
                users.append(user)
                print(f"✅ Kullanıcı oluşturuldu: {user.full_name}")
            else:
                users.append(user)
                print(f"⚠️  Kullanıcı zaten var: {user.full_name}")
        
        db.session.commit()
        
        # 2. Test İlanları Oluştur
        test_posts = [
            {
                'title': 'Ankara Adliyesi\'nde Duruşma Temsili',
                'description': 'Ankara 5. Asliye Hukuk Mahkemesi\'nde 25 Aralık 2024 tarihinde saat 10:30\'da duruşma vardır.\n\nDosya konusu: Alacak davası\nİş türü: Duruşmada taraf vekilliği\n\nGüncel dosya bilgileri tarafımızdan paylaşılacaktır.',
                'category': 'durusma',
                'urgency_level': 'urgent',
                'location': 'Ankara',
                'price_min': 1000,
                'price_max': 1500
            },
            {
                'title': 'İstanbul Çağlayan\'da Evrak Teslimi',
                'description': 'İstanbul Çağlayan Adliyesi 12. Ağır Ceza Mahkemesi\'ne evrak teslimi yapılacaktır.\n\nTeslim edilecek belgeler hazır durumda.\nAdres: Çağlayan Adalet Sarayı',
                'category': 'evrak_teslim',
                'urgency_level': 'normal',
                'location': 'İstanbul',
                'price_min': 500,
                'price_max': 750
            },
            {
                'title': 'İzmir Bölge İdare Mahkemesi\'nde Keşif',
                'description': 'İzmir Bölge İdare Mahkemesi\'nde keşif işlemi yapılacaktır.\n\nKeşif tarihi: 30 Aralık 2024\nKonu: İmar uygulaması',
                'category': 'kesif',
                'urgency_level': 'normal',
                'location': 'İzmir',
                'price_min': 2000,
                'price_max': 3000
            },
            {
                'title': 'Bursa\'da Tanık Dinleme',
                'description': 'Bursa 3. Asliye Ceza Mahkemesi\'nde tanık dinletilecektir.\n\nTarih: 5 Ocak 2025\nSaat: 11:00\nTanık sayısı: 2 kişi',
                'category': 'tanik_dinleme',
                'urgency_level': 'normal',
                'location': 'Bursa',
                'price_min': 800,
                'price_max': 1200
            },
            {
                'title': 'Antalya Asliye Hukuk\'ta Dilekçe Sunumu',
                'description': 'Antalya 7. Asliye Hukuk Mahkemesi\'ne dilekçe sunulacaktır.\n\nDilekçe hazır durumda.\nKonu: Tapu iptali davası',
                'category': 'dilekce',
                'urgency_level': 'very_urgent',
                'location': 'Antalya',
                'price_min': 600,
                'price_max': 900
            },
            {
                'title': 'İstanbul Anadolu Adliyesi Haciz İşlemi',
                'description': 'İstanbul Anadolu Adliyesi İcra Müdürlüğü\'nde haciz işlemi takip edilecektir.\n\nDosya no: 2024/1234\nAdres bilgileri mevcut.',
                'category': 'haciz',
                'urgency_level': 'urgent',
                'location': 'İstanbul',
                'price_min': 1500,
                'price_max': 2000
            },
            {
                'title': 'Ankara İcra Müdürlüğü\'nde Takip',
                'description': 'Ankara 15. İcra Müdürlüğü\'nde dosya takibi yapılacaktır.\n\nDosya: İcra takip dosyası\nİşlemler: Satış talep, itiraz',
                'category': 'diger',
                'urgency_level': 'normal',
                'location': 'Ankara',
                'price_min': 700,
                'price_max': 1000
            },
            {
                'title': 'İzmir Karşıyaka Adliyesi Duruşma',
                'description': 'İzmir Karşıyaka 2. Aile Mahkemesi\'nde boşanma davasında duruşma vardır.\n\nTarih: 8 Ocak 2025\nSaat: 09:30\nKonu: Boşanma ve velayet',
                'category': 'durusma',
                'urgency_level': 'normal',
                'location': 'İzmir',
                'price_min': 1200,
                'price_max': 1800
            },
            {
                'title': 'Gaziantep Adliyesi\'nde İcra Takibi',
                'description': 'Gaziantep İcra Müdürlüğü\'nde alacak takibi yapılacaktır.\n\nBorçlu bilgileri elimizde mevcut.',
                'category': 'diger',
                'urgency_level': 'urgent',
                'location': 'Gaziantep',
                'price_min': 900,
                'price_max': 1300
            },
            {
                'title': 'Adana Ticaret Mahkemesi\'nde Duruşma',
                'description': 'Adana 1. Ticaret Mahkemesi\'nde şirket alacağı davasında duruşma.\n\nTarih: 12 Ocak 2025\nSaat: 14:00',
                'category': 'durusma',
                'urgency_level': 'normal',
                'location': 'Adana',
                'price_min': 1500,
                'price_max': 2500
            }
        ]
        
        posts = []
        for i, post_data in enumerate(test_posts):
            # Rastgele bir kullanıcıyı ilan sahibi yap
            owner = random.choice(users)
            
            post = TevkilPost(
                user_id=owner.id,
                title=post_data['title'],
                description=post_data['description'],
                category=post_data['category'],
                urgency_level=post_data['urgency_level'],
                location=post_data['location'],
                price_min=post_data['price_min'],
                price_max=post_data['price_max'],
                remote_allowed=random.choice([True, False]),
                status='active',
                views=random.randint(10, 150),
                applications_count=random.randint(0, 8),
                expires_at=datetime.now(timezone.utc) + timedelta(days=random.randint(7, 30))
            )
            db.session.add(post)
            posts.append(post)
            print(f"✅ İlan oluşturuldu: {post.title}")
        
        db.session.commit()
        
        # 3. Test Başvuruları Oluştur
        for post in random.sample(posts, min(5, len(posts))):
            # Her ilana 1-3 başvuru ekle
            num_applications = random.randint(1, 3)
            applicants = random.sample([u for u in users if u.id != post.user_id], 
                                      min(num_applications, len(users) - 1))
            
            for applicant in applicants:
                application = Application(
                    post_id=post.id,
                    applicant_id=applicant.id,
                    message=f"Merhaba, {post.category} konusunda deneyimliyim. Bu işi üstlenebilirim.",
                    proposed_price=random.randint(int(post.price_min or 500), int(post.price_max or 2000)),
                    status=random.choice(['pending', 'pending', 'accepted', 'rejected'])
                )
                db.session.add(application)
                print(f"✅ Başvuru oluşturuldu: {applicant.full_name} -> {post.title}")
        
        db.session.commit()
        
        # 4. Test Değerlendirmeleri Oluştur
        for user in random.sample(users, min(4, len(users))):
            # Her kullanıcıya 1-3 değerlendirme ekle
            num_ratings = random.randint(1, 3)
            reviewers = random.sample([u for u in users if u.id != user.id], 
                                     min(num_ratings, len(users) - 1))
            
            for reviewer in reviewers:
                rating = Rating(
                    reviewed_id=user.id,
                    reviewer_id=reviewer.id,
                    rating=random.randint(4, 5),
                    comment=f"Harika bir iş çıkardı. Profesyonel ve güvenilir. Teşekkürler!",
                    post_id=random.choice(posts).id if posts else None
                )
                db.session.add(rating)
                print(f"✅ Değerlendirme oluşturuldu: {reviewer.full_name} -> {user.full_name}")
        
        db.session.commit()
        
        print("\n🎉 Test verileri başarıyla oluşturuldu!")
        print(f"\n📊 Özet:")
        print(f"   👥 Kullanıcılar: {len(users)}")
        print(f"   📋 İlanlar: {len(posts)}")
        print(f"   📝 Başvurular: {Application.query.count()}")
        print(f"   ⭐ Değerlendirmeler: {Rating.query.count()}")
        print(f"\n🔑 Test kullanıcı girişi:")
        print(f"   E-posta: ahmet.yilmaz@example.com")
        print(f"   Şifre: 123456")

if __name__ == '__main__':
    create_test_data()
