"""
Dinamik UDF test
"""
from udf_service_dynamic import create_authorization_udf_dynamic
import zipfile

# Test verileri
post_owner = {
    'name': 'Ayşe Demir',
    'baro': 'İstanbul Barosu',
    'sicil': '67890',
    'tax_office': 'Kadıköy V.D.',
    'tax_number': '1234567890',
    'address': 'Kadıköy/İstanbul Bağdat Caddesi No:150 Daire:5'
}

applicant = {
    'name': 'Ahmet Yılmaz',
    'baro': 'Ankara Barosu',
    'sicil': '12345',
    'tax_office': 'Çankaya V.D.',
    'tax_number': '0987654321',
    'address': 'Çankaya/Ankara Kızılay Mahallesi Atatürk Bulvarı No:10 Kat:3'
}

post_data = {
    'title': 'Test İlanı',
    'category': 'İcra',
    'location': 'Ankara',
    'description': 'Test açıklaması',
    'client_name': 'Mehmet Ali VELİ',
    'client_address': 'Keçiören/Ankara Test Mahallesi Sokak No:10',
    'vekaletname_info': '15.05.2024 tarih ve 1234 yevmiye nolu Ankara 5. Noterliği'
}

application_info = {
    'created_at': '20.10.2025',
    'accepted_at': '23.10.2025'
}

print("🔄 Dinamik UDF Test Başlıyor...")
print("-" * 70)

# UDF oluştur
udf_buffer = create_authorization_udf_dynamic(
    post_owner=post_owner,
    applicant=applicant,
    post=post_data,
    application=application_info,
    price=5000
)

# Kaydet
with open('dynamic_yetki_belgesi.udf', 'wb') as f:
    f.write(udf_buffer.getvalue())

print(f"✅ dynamic_yetki_belgesi.udf oluşturuldu!")
print(f"📦 Boyut: {len(udf_buffer.getvalue())} bytes")

# İçeriği kontrol et
udf_buffer.seek(0)
with zipfile.ZipFile(udf_buffer, 'r') as zf:
    content_xml = zf.read('content.xml').decode('utf-8')
    
    # CDATA içeriği
    cdata_start = content_xml.find('<![CDATA[') + 9
    cdata_end = content_xml.find(']]></content>')
    text_content = content_xml[cdata_start:cdata_end]
    
    print("\n" + "=" * 70)
    print("📄 DOLDURULMUŞ İÇERİK:")
    print("=" * 70)
    print(text_content)
    print("=" * 70)
    
    # Kontroller
    print("\n🔍 Kontroller:")
    
    checks = [
        ('Yetki veren adı', 'Ayşe Demir' in text_content),
        ('Yetki veren baro', 'İstanbul Barosu' in text_content),
        ('Yetki veren sicil', '67890' in text_content),
        ('Yetki veren vergi', 'Kadıköy V.D.' in text_content),
        ('Yetki veren adres (TAM)', 'Kadıköy/İstanbul Bağdat Caddesi No:150 Daire:5' in text_content),
        ('Başvuran baro', 'Ankara Barosu' in text_content),
        ('Başvuran sicil', '12345' in text_content),
        ('Başvuran adres (TAM)', 'Çankaya/Ankara Kızılay Mahallesi Atatürk Bulvarı No:10 Kat:3' in text_content),
        ('Müvekkil', 'Mehmet Ali VELİ' in text_content),
        ('Vekaletname', '15.05.2024' in text_content),
        ('Tarih', '23/10/2025' in text_content),
    ]
    
    all_ok = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}: {'OK' if result else 'HATA'}")
        if not result:
            all_ok = False
    
    print("\n" + "=" * 70)
    if all_ok:
        print("🎉 TÜM KONTROLLER BAŞARILI!")
        print("📝 ADRESLER TAM UZUNLUKTA GÖRÜNMELİ!")
    else:
        print("⚠️  BAZI KONTROLLER BAŞARISIZ!")
