"""
UYAP UDF formatında yetki belgesi oluşturma servisi

UDF = Universal Document Format (UYAP standardı)
- ZIP dosyası içinde content.xml
- XML formatında zengin metin desteği
- UYAP'ta doğrudan açılabilir ve imzalanabilir
- Şablon tabanlı doldurma sistemi
"""
from io import BytesIO
from datetime import datetime
import zipfile
import os


def create_authorization_udf(post_owner, applicant, post, application, price):
    """
    Şablon dosyasını kullanarak yetki belgesi UDF formatında oluştur
    
    ÖNEMLİ: UDF formatında character offset'ler çok kritik!
    - Şablondaki placeholder uzunluğu: 14 karakter (..............)
    - Değiştirilen metin de AYNI UZUNLUKTA olmalı
    - Aksi halde <elements> bölümündeki offset'ler kayar ve format bozulur
    
    Args:
        post_owner: İlan sahibi (yetki veren avukat) bilgileri
        applicant: Başvuran (yetkilendirilen avukat) bilgileri
        post: İlan bilgileri
        application: Başvuru bilgileri
        price: Kabul edilen fiyat
        
    Returns:
        BytesIO: UDF dosyası (ZIP formatında)
    """
    
    def pad_to_length(text, target_length=14):
        """
        Metni hedef uzunluğa tamamla (sağdan boşluk ekle)
        UYAP formatında placeholder uzunluğu korunmalı
        """
        text = str(text) if text else ''
        if len(text) > target_length:
            # Çok uzunsa kısalt
            return text[:target_length]
        # Kısa ise sağdan boşluk ekle
        return text + (' ' * (target_length - len(text)))
    
    # Şablon dosyası yolu
    template_path = os.path.join(os.path.dirname(__file__), 'OrnekVekaletnameYetkiBelgesiSablonu.udf')
    
    # Şablon dosyasını TAM OLARAK oku (elements dahil!)
    with zipfile.ZipFile(template_path, 'r') as template_zip:
        # Tüm XML'i al
        content_xml = template_zip.read('content.xml').decode('utf-8')
    
    # CDATA içeriğini çıkar
    cdata_start = content_xml.find('<![CDATA[') + 9
    cdata_end = content_xml.find(']]></content>')
    template_text = content_xml[cdata_start:cdata_end]
    
    # Bugünün tarihini al (../../.... formatında)
    current_date = datetime.now().strftime('%d/%m/%Y')
    
    # Metni doldur - UZUNLUK KORUMALI (14 karakter)
    filled_text = template_text
    
    # 1. AVUKATLIK ORTAKLIĞI (Yetki veren avukat adı) - 14 karakter
    filled_text = filled_text.replace('..............', pad_to_length(post_owner.get('name', '')), 1)
    
    # 2. Baro ve (Yetki veren) - 14 karakter
    filled_text = filled_text.replace('..............', pad_to_length(post_owner.get('baro', '')), 1)
    
    # 3. Sicil No (Yetki veren) - 14 karakter
    filled_text = filled_text.replace('..............', pad_to_length(post_owner.get('sicil', '')), 1)
    
    # Vergi Dairesi ve Sicil No (Yetki veren) - nokta yok, sonunda boşluk var
    vergi_veren = (post_owner.get('tax_office', '') + ' ' + post_owner.get('tax_number', '')).strip()
    if vergi_veren:
        filled_text = filled_text.replace('Vergi Dairesi ve Sicil No\t   :', f'Vergi Dairesi ve Sicil No\t   : {vergi_veren}', 1)
    
    # 4. Adres (Yetki veren) - 14 karakter
    filled_text = filled_text.replace('..............', pad_to_length(post_owner.get('address', '')), 1)
    
    # 5. Baro (Yetkilendirilen) - 14 karakter
    filled_text = filled_text.replace('..............', pad_to_length(applicant.get('baro', '')), 1)
    
    # 6. Sicil No (Yetkilendirilen) - 14 karakter
    filled_text = filled_text.replace('..............', pad_to_length(applicant.get('sicil', '')), 1)
    
    # Vergi Dairesi ve Sicil No (Yetkilendirilen) - nokta yok, sonunda tab var
    vergi_kilinan = (applicant.get('tax_office', '') + ' ' + applicant.get('tax_number', '')).strip()
    if vergi_kilinan:
        filled_text = filled_text.replace('Vergi Dairesi ve Sicil No\t   : \t', f'Vergi Dairesi ve Sicil No\t   : {vergi_kilinan}', 1)
    
    # 7. Adres (Yetkilendirilen) - 14 karakter
    filled_text = filled_text.replace('..............', pad_to_length(applicant.get('address', '')), 1)
    
    # VEKİL EDEN bilgileri (post sahibinin müvekkili)
    vekil_eden = post.get('client_name', '')
    if vekil_eden:
        filled_text = filled_text.replace('VEKİL EDEN\t\t  :', f'VEKİL EDEN\t\t  : {vekil_eden}', 1)
    
    # Adı Soyadı (vekil eden)
    if vekil_eden:
        filled_text = filled_text.replace('Adı Soyadı\t\t  :', f'Adı Soyadı\t\t  : {vekil_eden}', 1)
    
    # Adres (vekil eden) - üçüncü Adres alanı
    vekil_adres = post.get('client_address', '')
    if vekil_adres:
        # Bu satırda nokta yok, sadece : var
        filled_text = filled_text.replace('Adres\t\t  :', f'Adres\t\t  : {vekil_adres}', 1)
    
    # Dayanak Vekaletname bilgisi
    vekaletname = post.get('vekaletname_info', '')
    if vekaletname:
        filled_text = filled_text.replace('Noter Tarih ve Yevmiye No\t  : ', f'Noter Tarih ve Yevmiye No\t  : {vekaletname}', 1)
    
    # Tarih alanını doldur: ../../.... (10 karakter → tam eşleşmeli)
    filled_text = filled_text.replace('../../....', current_date)
    
    # İmza kısmındaki ismi doldur: "Av. ......................." 
    # Bu 23 nokta var, isimle değiştir ama uzunluğu koru
    signature_placeholder = 'Av. .......................'
    signature_text = f"Av. {post_owner.get('name', '')}"
    # İmza için padding (toplam 25 karakter: "Av. " + 21 karakter isim)
    signature_padded = signature_text + (' ' * max(0, len(signature_placeholder) - len(signature_text)))
    filled_text = filled_text.replace(signature_placeholder, signature_padded)
    
    # Yeni CDATA içeriğini XML'e yerleştir
    filled_xml = content_xml[:cdata_start] + filled_text + content_xml[cdata_end:]
    
    # Yeni UDF dosyasını oluştur
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('content.xml', filled_xml.encode('utf-8'))
    
    buffer.seek(0)
    return buffer
