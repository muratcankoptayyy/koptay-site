"""
GitHub Models AI Parser
OpenAI API uyumlu GitHub Models entegrasyonu
"""

import os
import json
import logging
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class GitHubModelsParser:
    """GitHub Models ile AI parsing (GPT-4o veya Claude 3.5 Sonnet)"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.model_name = os.getenv('GITHUB_MODEL', 'gpt-4o')  # veya 'claude-3.5-sonnet'
        
        if not self.github_token:
            logger.warning("⚠️ GITHUB_TOKEN bulunamadı!")
            return
        
        # GitHub Models endpoint (OpenAI uyumlu)
        self.client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=self.github_token
        )
        
        logger.info(f"✅ GitHub Models hazır: {self.model_name}")
    
    def is_ilan_message(self, message: str) -> bool:
        """
        Mesajın ilan mesajı olup olmadığını kontrol et
        
        Args:
            message: Kullanıcı mesajı
            
        Returns:
            bool: İlan mesajı ise True
        """
        # Kısa mesajlar muhtemelen ilan değil
        if len(message.strip()) < 20:
            return False
        
        # Ilan keywords
        keywords = [
            'mahkeme', 'duruşma', 'dava', 'tevkil', 'avukat', 
            'tl', 'lira', 'ücret', 'tarih', 'saat',
            'boşanma', 'ceza', 'ticaret', 'icra', 'miras',
            'asliye', 'ağır ceza'
        ]
        
        message_lower = message.lower()
        
        # En az 2 anahtar kelime içeriyorsa büyük ihtimalle ilan
        keyword_count = sum(1 for keyword in keywords if keyword in message_lower)
        
        return keyword_count >= 2
    
    def parse_natural_message(self, message_text: str) -> Dict:
        """
        Doğal dil mesajını parse et ve ilan bilgilerini çıkar
        
        Args:
            message_text: Kullanıcının mesajı
            
        Returns:
            dict: Parse edilmiş ilan bilgileri
        """
        if not self.github_token:
            return {
                'success': False,
                'error': 'GitHub token tanımlı değil'
            }
        
        prompt = f"""
Sen bir Türk avukat platformu için ilan mesajlarını analiz eden yapay zeka asistanısın.

Aşağıdaki mesajı analiz et ve ilan bilgilerini çıkar:

Mesaj: "{message_text}"

KURALLAR:
1. Başlık kısa ve öz olmalı (max 100 karakter)
2. Şehir adını bul (İstanbul, Ankara, İzmir, vs.)
3. Mahkeme adını tam bul
4. Kategori: boşanma, ceza, ticaret, icra, miras, vs.
5. Tarih ve saat bilgisini bul
6. Fiyat/ücret bilgisini bul (TL cinsinden)
7. Açıklama: Tüm önemli detayları içermeli

JSON formatında yanıt ver:
{{
    "success": true,
    "title": "İlan başlığı",
    "category": "kategori",
    "city": "şehir",
    "courthouse": "mahkeme adı",
    "date": "YYYY-MM-DD formatında",
    "time": "HH:MM formatında",
    "price": fiyat (sadece sayı),
    "description": "detaylı açıklama",
    "urgency": "normal veya urgent"
}}

Eğer bir bilgi bulunamazsa null dön.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Sen bir Türk hukuk platformu için mesaj analiz asistanısın. Her zaman JSON formatında yanıt verirsin."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # JSON parse et
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(result_text)
            
            logger.info(f"✅ AI Parse Başarılı: {result.get('title', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ AI parse hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def detect_user_intent(self, message: str) -> Dict:
        """
        Kullanıcı mesajının amacını belirle (onay/red/düzeltme)
        
        Args:
            message: Kullanıcı mesajı
            
        Returns:
            dict: {'intent': str, 'confidence': float}
        """
        if not self.github_token:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'error': 'GitHub token tanımlı değil'
            }
        
        prompt = f"""
Kullanıcının mesajını analiz et ve amacını belirle.

Mesaj: "{message}"

OLASI AMAÇLAR:
- approve: Onaylıyor, kabul ediyor (tamamdır, tamam, evet, paylaş, onayla, vs.)
- reject: Reddiyor, iptal ediyor (hayır, iptal, vazgeç, istemiyorum, vs.)
- correct: Düzeltme yapıyor (şehir X olmalı, fiyat Y olsun, vs.)
- question: Soru soruyor
- unknown: Belirsiz

JSON formatında yanıt ver:
{{
    "intent": "approve/reject/correct/question/unknown",
    "confidence": 0.0-1.0 arası güven skoru,
    "reasoning": "kısa açıklama"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Sen intent detection asistanısın. Her zaman JSON formatında yanıt verirsin."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            logger.error(f"❌ Intent detection hatası: {str(e)}")
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def extract_correction_from_message(self, message: str, pending_data: dict) -> dict:
        """
        Düzeltme mesajından bilgileri çıkar
        
        Args:
            message: Kullanıcı mesajı
            pending_data: Mevcut ilan bilgileri
            
        Returns:
            dict: Düzeltilmiş bilgiler
        """
        if not self.github_token:
            return pending_data
        
        prompt = f"""
Kullanıcı bir ilan bilgisini düzeltmek istiyor.

Mevcut ilan bilgileri:
{json.dumps(pending_data, ensure_ascii=False, indent=2)}

Kullanıcının düzeltme mesajı: "{message}"

Hangi alanları düzeltmek istiyor? Sadece değiştirilen alanları JSON olarak dön:

{{
    "title": "yeni başlık" (varsa),
    "city": "yeni şehir" (varsa),
    "price": yeni fiyat (varsa),
    "date": "yeni tarih" (varsa),
    "time": "yeni saat" (varsa),
    "description": "yeni açıklama" (varsa)
}}

Düzeltme yoksa boş obje dön: {{}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Sen düzeltme analiz asistanısın."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()
            
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            corrections = json.loads(result_text)
            
            # Mevcut data'yı güncelle
            updated_data = pending_data.copy()
            updated_data.update(corrections)
            
            return updated_data
            
        except Exception as e:
            logger.error(f"❌ Correction parse hatası: {str(e)}")
            return pending_data


# Test fonksiyonu
def test_github_models():
    """GitHub Models'i test et"""
    from dotenv import load_dotenv
    load_dotenv()
    
    parser = GitHubModelsParser()
    
    print("\n🤖 GitHub Models AI Parser Test\n")
    
    # Test 1: Doğal dil parsing
    print("Test 1: Doğal dil parsing...")
    test_mesaj = "İzmir 3. Aile Mahkemesinde yarın saat 14:00 boşanma davası duruşması var. 4000 TL teklif ediyorum."
    result = parser.parse_natural_message(test_mesaj)
    print(f"Sonuç: {json.dumps(result, ensure_ascii=False, indent=2)}\n")
    
    # Test 2: Intent detection
    print("Test 2: Intent detection...")
    intent_result = parser.detect_user_intent("Tamamdır, paylaşabilirsin")
    print(f"Sonuç: {json.dumps(intent_result, ensure_ascii=False, indent=2)}\n")
    
    # Test 3: Correction
    print("Test 3: Correction extraction...")
    pending = {"city": "İzmir", "price": 4000}
    correction_result = parser.extract_correction_from_message("Şehir İstanbul olmalı", pending)
    print(f"Sonuç: {json.dumps(correction_result, ensure_ascii=False, indent=2)}\n")


if __name__ == '__main__':
    test_github_models()
