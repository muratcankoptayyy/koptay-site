"""
Gerçek veri ile dinamik UDF testi
"""
from app import app, db, TevkilPost, Application
from udf_service_dynamic import create_authorization_udf_dynamic
from datetime import datetime
import zipfile

with app.app_context():
    # İlanı bul
    post = TevkilPost.query.first()
    application = Application.query.filter_by(post_id=post.id, status='accepted').first()
    
    print(f"📋 İlan: {post.title}")
    print(f"   Sahibi: {post.user.full_name}")
    print(f"   Başvuran: {application.applicant.full_name}")
    
    # Verileri hazırla
    post_owner = {
        'name': post.user.full_name,
        'baro': post.user.bar_association or '',
        'tc_number': post.user.tc_number or '',
        'sicil': post.user.bar_registration_number or '',
        'tax_office': '',
        'tax_number': '',
        'address': post.user.address or ''
    }
    
    applicant_data = {
        'name': application.applicant.full_name,
        'baro': application.applicant.bar_association or '',
        'tc_number': application.applicant.tc_number or '',
        'sicil': application.applicant.bar_registration_number or '',
        'tax_office': '',
        'tax_number': '',
        'address': application.applicant.address or ''
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
        'created_at': application.created_at.strftime('%d.%m.%Y %H:%M') if application.created_at else '',
        'accepted_at': application.updated_at.strftime('%d.%m.%Y %H:%M') if application.updated_at else ''
    }
    
    print("\n🔄 Dinamik UDF oluşturuluyor...")
    
    # UDF oluştur
    udf_buffer = create_authorization_udf_dynamic(
        post_owner=post_owner,
        applicant=applicant_data,
        post=post_data,
        application=application_info,
        price=application.proposed_price or 0
    )
    
    # Kaydet
    filename = f"real_dynamic_{post.user.full_name}_{application.applicant.full_name}.udf"
    with open(filename, 'wb') as f:
        f.write(udf_buffer.getvalue())
    
    print(f"✅ {filename} oluşturuldu!")
    print(f"📦 Boyut: {len(udf_buffer.getvalue())} bytes")
    
    # İçeriği göster
    udf_buffer.seek(0)
    with zipfile.ZipFile(udf_buffer, 'r') as zf:
        content_xml = zf.read('content.xml').decode('utf-8')
        cdata_start = content_xml.find('<![CDATA[') + 9
        cdata_end = content_xml.find(']]></content>')
        text_content = content_xml[cdata_start:cdata_end]
        
        print("\n" + "=" * 70)
        print("📄 İÇERİK:")
        print("=" * 70)
        print(text_content[:1000])
        print("=" * 70)
        
        print("\n✅ DİNAMİK UDF SİSTEMİ ÇALIŞIYOR!")
        print("📝 Adresler tam uzunlukta görünmeli")
        print(f"\n🎯 UYAP'ta açın: {filename}")
