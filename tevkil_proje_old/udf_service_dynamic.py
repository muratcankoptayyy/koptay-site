"""
UYAP UDF formatında yetki belgesi oluşturma servisi (D İNAMİK ELEMENTS)

UDF = Universal Document Format (UYAP standardı)
- ZIP dosyası içinde content.xml
- XML formatında <elements> bölümü dinamik olarak oluşturulmalı
- Her satır için offset ve length hesaplanır
"""
from io import BytesIO
from datetime import datetime
import zipfile
import os


def create_authorization_udf_dynamic(post_owner, applicant, post, application, price):
    """
    Yetki belgesini UYAP UDF formatında oluştur (dinamik elements ile)
    
    Şablon kullanmak yerine, metni ve formatlamayı dinamik oluşturur
    Bu sayede uzunluk sınırlaması olmaz ve elements offset'leri doğru olur
    """
    current_date = datetime.now().strftime('%d/%m/%Y')
    
    # Yetki belgesi metni
    content_lines = [
        "YETKİ BELGESİ",
        "",
        "YETKİ BELGESİ VEREN AVUKAT",
        "",
        f"AVUKATLIK ORTAKLIĞI\t   : {post_owner.get('name', '')}",
        f"Baro ve \t\t   : {post_owner.get('baro', '')}",
        f"Sicil No \t\t   : {post_owner.get('sicil', '')}",
        f"Vergi Dairesi ve Sicil No\t   : {(post_owner.get('tax_office', '') + ' ' + post_owner.get('tax_number', '')).strip()}",
        f"Adres\t\t   : {post_owner.get('address', '')}",
        "",
        "YETKİLİ KILINAN AVUKAT: ",
        f"Baro \t\t   : {applicant.get('baro', '')}",
        f"Sicil No \t\t   : {applicant.get('sicil', '')}",
        f"Vergi Dairesi ve Sicil No\t   : {(applicant.get('tax_office', '') + ' ' + applicant.get('tax_number', '')).strip()}",
        f"Adres\t\t   : {applicant.get('address', '')}",
        "",
        f"VEKİL EDEN\t\t  : {post.get('client_name', '')}",
        "",
        f"Adı Soyadı\t\t  : {post.get('client_name', '')}",
        f"Adres\t\t  : {post.get('client_address', '')}",
        "",
        "",
        "Dayanak Vekaletname/Vekaletnameler",
        f"Noter Tarih ve Yevmiye No\t  : {post.get('vekaletname_info', '')}",
        "",
        "YETKİ BELGESİNİN KAPSAMI\t:",
        "",
        f"Bu yetki belgesi, 1136 sayılı Avukatlık Kanunu'nu değiştiren 4667 sayılı Kanun'un 36. maddesi ile 56. maddesine eklenen hüküm uyarınca, vekaletname yerine geçmek üzere, SADECE DURUŞMALARA KATILMA YETKİSİYLE SINIRLI OLMAK ÜZERE tarafımdan düzenlenmiştir. {current_date}",
        "",
        "",
        "",
        "",
        "",
        f"\t\t\t\t       Av. {post_owner.get('name', '')}",
        "",
        "\t\t\t\t       (e-imzalıdır)",
        "",
        "",
    ]
    
    # Metni birleştir
    full_content = '\n'.join(content_lines)
    
    # XML escape (CDATA için)
    def escape_xml_cdata(text):
        return text.replace(']]>', ']]]]><![CDATA[>')
    
    escaped_content = escape_xml_cdata(full_content)
    
    # Elements oluştur (dinamik offset calculation)
    paragraphs_xml = []
    offset = 0
    
    for i, line in enumerate(content_lines):
        line_length = len(line) + 1  # +1 for newline
        
        if line.strip():
            # Başlık kontrolü
            if i == 0:  # "YETKİ BELGESİ"
                paragraphs_xml.append(
                    f'<paragraph Alignment="1"><content bold="true" size="14" startOffset="{offset}" length="{len(line)}" />'
                    f'<content startOffset="{offset + len(line)}" length="1" /></paragraph>'
                )
            elif i == 2:  # "YETKİ BELGESİ VEREN AVUKAT"
                paragraphs_xml.append(
                    f'<paragraph LineSpacing="0.14999998"><content startOffset="{offset}" length="{line_length}" /></paragraph>'
                )
            elif line.startswith('AVUKATLIK') or line.startswith('Baro') or line.startswith('Sicil') or line.startswith('Vergi') or line.startswith('Adres'):
                # Veri satırları
                paragraphs_xml.append(
                    f'<paragraph LineSpacing="0.14999998"><content startOffset="{offset}" length="{line_length}" /></paragraph>'
                )
            elif 'YETKİLİ KILINAN' in line:
                paragraphs_xml.append(
                    f'<paragraph LineSpacing="0.14999998"><content startOffset="{offset}" length="{line_length}" /></paragraph>'
                )
            elif line.startswith('VEKİL') or line.startswith('Adı Soyadı'):
                paragraphs_xml.append(
                    f'<paragraph LineSpacing="0.14999998"><content startOffset="{offset}" length="{line_length}" /></paragraph>'
                )
            elif 'Dayanak' in line or 'Noter' in line:
                paragraphs_xml.append(
                    f'<paragraph LineSpacing="0.14999998"><content startOffset="{offset}" length="{line_length}" /></paragraph>'
                )
            elif 'KAPSAMI' in line:
                paragraphs_xml.append(
                    f'<paragraph LineSpacing="0.14999998"><content startOffset="{offset}" length="{line_length}" /></paragraph>'
                )
            elif line.startswith('Bu yetki belgesi'):
                # Uzun paragraf - "SADECE DURUŞMALARA..." kısmı bold olmalı
                # Bold başlangıcı: 169, uzunluk: 57
                bold_start_in_line = 169
                bold_length = 57
                paragraphs_xml.append(
                    f'<paragraph Alignment="3" LineSpacing="0.14999998">'
                    f'<content startOffset="{offset}" length="{bold_start_in_line}" />'
                    f'<content bold="true" startOffset="{offset + bold_start_in_line}" length="{bold_length}" />'
                    f'<content startOffset="{offset + bold_start_in_line + bold_length}" length="{len(line) - bold_start_in_line - bold_length}" />'
                    f'<content startOffset="{offset + len(line)}" length="1" /></paragraph>'
                )
            elif line.strip().startswith('Av.') or '(e-imzalıdır)' in line:
                # İmza satırları - sağa yasla
                paragraphs_xml.append(
                    f'<paragraph Alignment="2"><content startOffset="{offset}" length="{line_length}" /></paragraph>'
                )
            else:
                # Normal paragraf
                paragraphs_xml.append(
                    f'<paragraph><content startOffset="{offset}" length="{line_length}" /></paragraph>'
                )
        else:
            # Boş satır
            paragraphs_xml.append(
                f'<paragraph><content startOffset="{offset}" length="1" /></paragraph>'
            )
        
        offset += line_length
    
    elements_content = '\n'.join(paragraphs_xml)
    
    # XML oluştur
    content_xml = f'''<?xml version="1.0" encoding="UTF-8" ?> 

<template format_id="1.8" >
<content><![CDATA[{escaped_content}]]></content><properties><pageFormat mediaSizeName="1" leftMargin="70.8661413192749" rightMargin="70.8661413192749" topMargin="70.8661413192749" bottomMargin="70.8661413192749" paperOrientation="1" headerFOffset="20.0" footerFOffset="20.0" /></properties>
<elements resolver="hvl-default" >
{elements_content}
</elements>
<styles><style name="default" description="Geçerli" family="Dialog" size="12" bold="false" italic="false" FONT_ATTRIBUTE_KEY="javax.swing.plaf.FontUIResource[family=Dialog,name=Dialog,style=plain,size=12]" foreground="-13421773" /><style name="hvl-default" family="Times New Roman" size="12" description="Gövde" /></styles>
</template>'''
    
    # ZIP buffer
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('content.xml', content_xml.encode('utf-8'))
    
    buffer.seek(0)
    return buffer
