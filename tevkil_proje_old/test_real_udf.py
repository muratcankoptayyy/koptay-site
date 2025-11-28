"""
Gerçek veri ile UDF testi
"""
from app import app, db, TevkilPost, Application, User
from udf_service import create_authorization_udf
from datetime import datetime

with app.app_context():
    # İlk ilanı bul
    post = TevkilPost.query.first()
    if not post:
        print("❌ Test ilanı yok!")
        exit(1)
    
    print(f"📋 İlan: {post.title}")
    print(f"   Sahibi: {post.user.full_name}")
    print(f"   Baro: {post.user.bar_association}")
    print(f"   Sicil: {post.user.bar_registration_number}")
    print(f"   Adres: {post.user.address}")
    
    # Kabul edilmiş başvuru bul
    application = Application.query.filter_by(post_id=post.id, status='accepted').first()
    
    if not application:
        print("\n⚠️  Kabul edilmiş başvuru yok, ilk başvuruyu kullanıyorum...")
        application = Application.query.filter_by(post_id=post.id).first()
        
    if not application:
        print("❌ Hiç başvuru yok!")
        exit(1)
    
    print(f"\n✅ Başvuru: #{application.id}")
    print(f"   Başvuran: {application.applicant.full_name}")
    print(f"   Baro: {application.applicant.bar_association}")
    print(f"   Sicil: {application.applicant.bar_registration_number}")
    print(f"   Adres: {application.applicant.address}")
    
    # Verileri hazırla (app.py'deki gibi)
    post_owner = {
        'name': post.user.full_name,
        'baro': post.user.bar_association or 'Belirtilmemiş',
        'tc_number': post.user.tc_number or '',
        'sicil': post.user.bar_registration_number or 'Belirtilmemiş',
        'tax_office': '',
        'tax_number': '',
        'address': post.user.address or 'Belirtilmemiş'
    }
    
    applicant_data = {
        'name': application.applicant.full_name,
        'baro': application.applicant.bar_association or 'Belirtilmemiş',
        'tc_number': application.applicant.tc_number or '',
        'sicil': application.applicant.bar_registration_number or 'Belirtilmemiş',
        'tax_office': '',
        'tax_number': '',
        'address': application.applicant.address or 'Belirtilmemiş'
    }
    
    post_data = {
        'title': post.title,
        'category': post.category,
        'location': post.location,
        'description': post.description,
        'client_name': '',
        'client_address': '',
        'vekaletname_info': ''
    }
    
    application_info = {
        'created_at': application.created_at.strftime('%d.%m.%Y %H:%M') if application.created_at else 'Belirtilmemiş',
        'accepted_at': application.updated_at.strftime('%d.%m.%Y %H:%M') if application.updated_at else 'Belirtilmemiş'
    }
    
    print("\n🔄 UDF oluşturuluyor...")
    
    # UDF oluştur
    udf_buffer = create_authorization_udf(
        post_owner=post_owner,
        applicant=applicant_data,
        post=post_data,
        application=application_info,
        price=application.proposed_price or 0
    )
    
    # Dosyaya kaydet
    filename = f"real_yetki_belgesi_{post.user.full_name}_{application.applicant.full_name}.udf"
    with open(filename, 'wb') as f:
        f.write(udf_buffer.getvalue())
    
    print(f"✅ {filename} oluşturuldu!")
    print(f"📦 Boyut: {len(udf_buffer.getvalue())} bytes")
    
    # İçeriği kontrol et
    import zipfile
    udf_buffer.seek(0)
    with zipfile.ZipFile(udf_buffer, 'r') as zf:
        content_xml = zf.read('content.xml').decode('utf-8')
        cdata_start = content_xml.find('<![CDATA[') + 9
        cdata_end = content_xml.find(']]></content>')
        text_content = content_xml[cdata_start:cdata_end]
        
        print("\n" + "=" * 70)
        print("📄 DOLDURULMUŞ İÇERİK (İLK 1500 KARAKTER):")
        print("=" * 70)
        print(text_content[:1500])
        print("=" * 70)
        
        # Kontrol
        print("\n🔍 Kontroller:")
        if post.user.full_name in text_content:
            print(f"✅ Yetki veren adı bulundu: {post.user.full_name}")
        else:
            print(f"❌ Yetki veren adı BULUNAMADI: {post.user.full_name}")
            
        if application.applicant.full_name in text_content:
            print(f"✅ Başvuran adı bulundu: {application.applicant.full_name}")
        else:
            print(f"❌ Başvuran adı BULUNAMADI: {application.applicant.full_name}")
            
        if '..............' in text_content:
            print("❌ BOŞ NOKTA ALANLARI VAR!")
        else:
            print("✅ Tüm nokta alanları dolduruldu")
            
        if 'Belirtilmemiş' in text_content:
            count = text_content.count('Belirtilmemiş')
            print(f"⚠️  {count} adet 'Belirtilmemiş' bulundu")
        else:
            print("✅ 'Belirtilmemiş' yok")
