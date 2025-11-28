"""
Gemini AI ile Doğal Dil İlan Parser
Avukatların serbest yazdığı mesajları yapılandırılmış ilan formatına çevirir
"""
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ google-generativeai kütüphanesi yüklü değil")


class GeminiIlanParser:
    """Gemini AI ile doğal dil mesajlarını ilan formatına çevirir"""
    
    def __init__(self):
        """Gemini AI'yi yapılandır"""
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai kütüphanesi gerekli: pip install google-generativeai")
        
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable bulunamadı")
        
        genai.configure(api_key=self.api_key)
        
        # Gemini 2.5 Flash veya Pro model kullan
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        self.model = genai.GenerativeModel(model_name)
        
        print(f"✅ Gemini AI hazır: {model_name}")
    
    def parse_natural_message(self, message_text):
        """
        Doğal dil mesajını yapılandırılmış ilan formatına çevir
        
        Args:
            message_text (str): Avukatın yazdığı serbest metin
            
        Returns:
            dict: {
                'success': bool,
                'title': str,
                'city': str,
                'courthouse': str,
                'description': str,
                'price': int,
                'raw_message': str
            }
        """
        
        # AI'ye gönderilecek prompt
        prompt = f"""Sen bir Türk hukuk asistanısın. Avukatların yazdığı mesajları analiz edip yapılandırılmış ilan formatına çeviriyorsun.

GÖREV: Aşağıdaki mesajı analiz et ve JSON formatında ilan bilgilerini çıkar.

MESAJ:
{message_text}

ÇIKARILACAK BİLGİLER:
1. **Başlık**: İlanın kısa başlığı (örn: "Boşanma Davası Duruşması", "Aile Mahkemesi Tevkili")
2. **Şehir**: Mahkemenin bulunduğu şehir (İstanbul, Ankara, İzmir vb.)
3. **Mahkeme**: Tam mahkeme adı (örn: "İstanbul 5. Aile Mahkemesi")
4. **Açıklama**: İlanın detaylı açıklaması (duruşma saati, tarih, özel notlar vb.)
5. **Ücret**: Teklif edilen ücret (TL cinsinden, belirtilmemişse 0)

KURALLAR:
- Mahkeme adını tam ve doğru yaz
- Şehir adını büyük harfle başlat
- Açıklamaya tüm önemli detayları ekle (saat, tarih, özel notlar)
- Ücret belirtilmemişse 0 yaz
- Başlığı kısa ve öz tut (max 50 karakter)

ÇIKTI FORMATI (sadece JSON, başka bir şey yazma):
{{
  "title": "Başlık buraya",
  "city": "Şehir adı",
  "courthouse": "Mahkeme tam adı",
  "description": "Detaylı açıklama",
  "price": 5000
}}

Şimdi yukarıdaki mesajı analiz et ve SADECE JSON çıktısını ver:"""

        try:
            # Gemini AI'den yanıt al
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # JSON yanıtı parse et
            # Eğer markdown code block içindeyse temizle
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            # JSON parse
            parsed_data = json.loads(response_text)
            
            # Validasyon
            required_fields = ['title', 'city', 'courthouse', 'description', 'price']
            for field in required_fields:
                if field not in parsed_data:
                    raise ValueError(f"Eksik alan: {field}")
            
            # Başarılı parse
            result = {
                'success': True,
                'title': parsed_data['title'][:100],  # Max 100 karakter
                'city': parsed_data['city'],
                'courthouse': parsed_data['courthouse'],
                'description': parsed_data['description'],
                'price': int(parsed_data['price']),
                'raw_message': message_text
            }
            
            print(f"✅ AI Parse Başarılı:")
            print(f"   Başlık: {result['title']}")
            print(f"   Şehir: {result['city']}")
            print(f"   Mahkeme: {result['courthouse']}")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse hatası: {str(e)}")
            print(f"AI Yanıtı: {response_text}")
            return {
                'success': False,
                'error': 'AI yanıtı JSON formatında değil',
                'raw_response': response_text
            }
        except Exception as e:
            print(f"❌ AI parse hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def is_ilan_message(self, message_text):
        """
        Mesajın ilan olup olmadığını kontrol et
        
        Anahtar kelimeler: mahkeme, duruşma, tevkil, vekil, dava, müvekkil vb.
        """
        keywords = [
            'mahkeme', 'duruşma', 'tevkil', 'vekil', 'dava', 
            'müvekkil', 'celse', 'karar', 'dosya', 'icra',
            'avukat', 'savunma', 'dilekçe', 'hukuk', 'ceza',
            'aile', 'ticaret', 'iş', 'icra', 'iflas'
        ]
        
        message_lower = message_text.lower()
        
        # En az bir anahtar kelime içermeli
        for keyword in keywords:
            if keyword in message_lower:
                return True
        
        return False
    
    def detect_user_intent(self, message: str) -> dict:
        """
        Kullanıcının mesajındaki niyeti algıla (onay/red/düzeltme)
        TAM DOĞAL DİL - keyword kontrolü yok, her şey AI'ya
        
        Returns:
            dict: {
                'intent': 'approve'|'reject'|'correction'|'question'|'unknown',
                'confidence': 0.0-1.0,
                'message': str
            }
        """
        # Direkt Gemini'ye sor - keyword kontrolü yapma!
        # AI dil nüanslarını çok daha iyi anlıyor
        return self._ask_gemini_intent(message)
    
    def _ask_gemini_intent(self, message: str) -> dict:
        """
        Gemini AI'ya kullanıcının niyetini sor - TAM DOĞAL DİL
        """
        prompt = f"""Kullanıcı bir ilan önizlemesi gördü ve yanıt veriyor. Niyetini belirle.

KULLANICI MESAJI: "{message}"

Kullanıcı ne demek istiyor? Sadece JSON formatında cevap ver:

{{
  "intent": "approve",
  "confidence": 0.95
}}

İNTENT DEĞERLERİ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. "approve" - İlanı onaylıyor, yayınlamak istiyor
   Örnekler: 
   ✓ "Evet", "Tamam", "Olur", "Güzel", "Tamamdır"
   ✓ "Paylaş", "Yayınla", "Gönder", "Hadi"
   ✓ "Süper", "Harika", "Perfect", "İyi olmuş"
   ✓ "Doğru", "Aynen", "Kabul", "OK"
   ✓ "Hepsi doğru", "Evet paylaş", "Tamam gönder"
   
2. "reject" - İlanı reddediyor, iptal etmek istiyor
   Örnekler:
   ✓ "Hayır", "İptal", "Vazgeç", "İstemiyorum"
   ✓ "Sil", "Yapma", "Olmadı", "Bırak"
   
3. "correction" - Düzeltme yapmak istiyor
   Örnekler:
   ✓ "Şehir İstanbul olmalı"
   ✓ "Ücret 4000 TL"
   ✓ "Yanlış, Ankara değil İzmir"
   ✓ "Mahkeme adı hatalı"
   ✓ "Saat 14:00 olacak"
   
4. "question" - Soru soruyor veya anlamadı
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ÖNEMLİ: Türkçe'nin nüanslarını anla. "Paylaş" = onay, "Tamamdır" = onay, "Hadi gönder" = onay.

Confidence: 0.0-1.0 (yüksek güven = açık intent, düşük = belirsiz)

SADECE JSON, başka açıklama yazma."""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # JSON parse et
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            return {
                'intent': result.get('intent', 'unknown'),
                'confidence': float(result.get('confidence', 0.5)),
                'message': message
            }
        except Exception as e:
            print(f"⚠️ Gemini intent hatası: {e}")
        
        return {
            'intent': 'unknown',
            'confidence': 0.0,
            'message': message
        }
    
    def extract_correction_from_message(self, message: str, pending_data: dict) -> dict:
        """
        Kullanıcının düzeltme mesajından hangi alanı değiştirmek istediğini çıkar
        
        Args:
            message: Kullanıcının düzeltme mesajı (örn: "Şehir İstanbul olmalı", "Ücret 3000 TL")
            pending_data: Mevcut ilan bilgileri
        
        Returns:
            dict: Güncellenmiş ilan bilgileri
        """
        prompt = f"""Kullanıcı bir ilan önizlemesi gördü ve düzeltme yapmak istiyor.

MEVCUT İLAN BİLGİLERİ:
- Başlık: {pending_data.get('title', '')}
- Mahkeme: {pending_data.get('courthouse', '')}
- Şehir: {pending_data.get('city', '')}
- Açıklama: {pending_data.get('description', '')}
- Ücret: {pending_data.get('price', '')} TL

KULLANICI MESAJI:
"{message}"

Kullanıcı hangi bilgiyi değiştirmek istiyor? Değişikliği uygula ve GÜNCELLENMİŞ bilgileri döndür.

Sadece JSON formatında cevap ver:
{{
  "title": "güncellenmiş veya aynı başlık",
  "courthouse": "güncellenmiş veya aynı mahkeme",
  "city": "güncellenmiş veya aynı şehir",
  "description": "güncellenmiş veya aynı açıklama",
  "price": "güncellenmiş veya aynı ücret (sadece sayı)",
  "changed_field": "hangi alan değişti (title/courthouse/city/description/price)",
  "change_summary": "Şehir Ankara'dan İstanbul'a değiştirildi gibi kısa açıklama"
}}

Sadece JSON, başka yazı yazma."""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # JSON parse et
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            
            return {
                'success': True,
                'title': result.get('title', pending_data.get('title')),
                'courthouse': result.get('courthouse', pending_data.get('courthouse')),
                'city': result.get('city', pending_data.get('city')),
                'description': result.get('description', pending_data.get('description')),
                'price': result.get('price', pending_data.get('price')),
                'changed_field': result.get('changed_field', 'unknown'),
                'change_summary': result.get('change_summary', 'Bilgi güncellendi')
            }
        except Exception as e:
            print(f"❌ Düzeltme parse hatası: {e}")
            return {
                'success': False,
                'error': f"Düzeltmeyi anlayamadım. Lütfen daha açık yazın: {str(e)}"
            }
        
        return {
            'success': False,
            'error': "Düzeltme yapılamadı"
        }


# Test fonksiyonu
def test_gemini_parser():
    """Gemini parser'ı test et"""
    
    test_messages = [
        "İstanbul 5. Aile Mahkemesi Duruşmasına katılım için bir meslektaş araşımız bulunmaktadır duruşma saati 10.00",
        "Ankara 2. Ağır Ceza Mahkemesinde yarın saat 14:00'te duruşmam var, 3000 TL karşılığında tevkil arıyorum",
        "Kadıköy İcra Müdürlüğünde dosya takibi yapacak meslektaş lazım, 2500 TL ücret"
    ]
    
    parser = GeminiIlanParser()
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}:")
        print(f"Mesaj: {msg}")
        print(f"{'='*60}")
        
        result = parser.parse_natural_message(msg)
        
        if result['success']:
            print(f"\n✅ BAŞARILI PARSE:")
            print(f"📋 Başlık: {result['title']}")
            print(f"🏛️ Şehir: {result['city']}")
            print(f"⚖️ Mahkeme: {result['courthouse']}")
            print(f"📝 Açıklama: {result['description']}")
            print(f"💰 Ücret: {result['price']} TL")
        else:
            print(f"\n❌ PARSE BAŞARISIZ:")
            print(f"Hata: {result.get('error', 'Bilinmeyen hata')}")


if __name__ == '__main__':
    # Test
    if GEMINI_AVAILABLE and os.getenv('GEMINI_API_KEY'):
        test_gemini_parser()
    else:
        print("❌ Gemini API key bulunamadı veya kütüphane yüklü değil")
        print("Ayarlamak için:")
        print("1. pip install google-generativeai")
        print("2. .env dosyasına GEMINI_API_KEY ekleyin")
