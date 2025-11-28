# 🤖 Gemini AI - Doğal Dil İlan Parser Kurulumu

## 🎯 Özellik

Avukatlar artık **doğal dil** ile ilan oluşturabilir! Şablon kullanmaya gerek yok.

### ✅ Önce:
```
#ILAN
Başlık: Boşanma Davası
Şehir: İstanbul
Mahkeme: İstanbul 5. Aile Mahkemesi
Açıklama: Yarın saat 10:00 duruşma
Ücret: 3000
```

### 🚀 Şimdi:
```
İstanbul 5. Aile Mahkemesi'nde yarın saat 10:00 duruşmam var, 
tevkil arıyorum, 3000 TL ücret teklif ediyorum
```

AI otomatik olarak:
- Mahkeme adını bulur
- Şehri tespit eder
- Başlık oluşturur
- Açıklama düzenler
- Ücreti çıkarır

---

## 📋 Kurulum Adımları

### 1️⃣ Gemini API Key Alın

1. Google AI Studio'ya gidin:
   https://aistudio.google.com/app/apikey

2. "Create API Key" butonuna tıklayın

3. Yeni proje oluşturun veya mevcut projeyi seçin

4. API key'i kopyalayın (örn: `AIzaSyA...`)

### 2️⃣ .env Dosyasına Ekleyin

`.env` dosyasını açın ve şunu ekleyin/güncelleyin:

```env
# Gemini AI (Doğal dil ilan parser için)
GEMINI_API_KEY=AIzaSyAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_MODEL=gemini-2.0-flash-exp
```

**Modeller:**
- `gemini-2.0-flash-exp` - En hızlı, ücretsiz (ÖNERİLİR)
- `gemini-2.5-flash-preview-0514` - Daha gelişmiş
- `gemini-1.5-pro` - En güçlü (ücretli)

### 3️⃣ Test Edin

Terminal'de:

```powershell
python gemini_ai_parser.py
```

Başarılı test çıktısı:
```
✅ Gemini AI hazır: gemini-2.0-flash-exp
✅ AI Parse Başarılı:
   Başlık: İstanbul 5. Aile Mahkemesi Duruşması
   Şehir: İstanbul
   Mahkeme: İstanbul 5. Aile Mahkemesi
```

### 4️⃣ Flask'ı Yeniden Başlatın

AI parser aktif olsun diye:

```powershell
# Eski Flask'ı kapat (Ctrl+C)
# Yeniden başlat:
python run_flask.py
```

Başarılı log:
```
✅ Gemini AI parser aktif - doğal dil ilanları destekleniyor
```

---

## 💬 Kullanım Örnekleri

### Örnek 1: Basit Duruşma
**Mesaj:**
```
Ankara 2. Ağır Ceza Mahkemesinde yarın saat 14:00'te duruşmam var, 
3000 TL karşılığında tevkil arıyorum
```

**AI Çıktısı:**
- Başlık: "Ankara 2. Ağır Ceza Duruşma Temsili"
- Şehir: Ankara
- Mahkeme: Ankara 2. Ağır Ceza Mahkemesi
- Açıklama: "Yarın saat 14:00 duruşma temsili"
- Ücret: 3000 TL

### Örnek 2: İcra Takibi
**Mesaj:**
```
Kadıköy İcra Müdürlüğünde dosya takibi yapacak meslektaş lazım, 2500 TL ücret
```

**AI Çıktısı:**
- Başlık: "Kadıköy İcra Dosya Takibi"
- Şehir: İstanbul
- Mahkeme: Kadıköy İcra Müdürlüğü
- Açıklama: "Dosya takibi"
- Ücret: 2500 TL

### Örnek 3: Şablonlu Hala Çalışır
**Mesaj:**
```
#ILAN
Başlık: Test
Şehir: İzmir
Açıklama: Test ilan
Ücret: 1000
```

✅ Eski sistem de çalışmaya devam eder!

---

## 🔍 Nasıl Çalışır?

1. **Mesaj Gelir:** "İstanbul 5. Aile Mahkemesi'nde..."
2. **Anahtar Kelime Kontrolü:** mahkeme, duruşma, tevkil, vekil, dava...
3. **AI Parse:** Gemini 2.0 Flash mesajı analiz eder
4. **JSON Çıktı:** title, city, courthouse, description, price
5. **İlan Oluştur:** Otomatik database'e kaydedilir
6. **Onay Mesajı:** Kullanıcıya gönderilir

---

## ⚙️ Ayarlar

### Model Değiştirme

`.env` dosyasında:

```env
# Hızlı, ücretsiz (günde 1500 istek)
GEMINI_MODEL=gemini-2.0-flash-exp

# Daha güçlü (günde 50 istek)
GEMINI_MODEL=gemini-1.5-pro
```

### AI Kapatma

Sadece şablonlu mod kullanmak için:

```env
# Bu satırı silin veya yorum yapın:
# GEMINI_API_KEY=...
```

Bot otomatik olarak sadece `#ILAN` komutunu destekler.

---

## 🐛 Sorun Giderme

### Hata: "GEMINI_API_KEY bulunamadı"

**Çözüm:** `.env` dosyasına key ekleyin:
```env
GEMINI_API_KEY=AIzaSyA...
```

### Hata: "google-generativeai kütüphanesi yüklü değil"

**Çözüm:**
```powershell
pip install google-generativeai
```

### Hata: "AI mesajı parse edemedi"

**Sebep:** Mesaj çok kısa veya belirsiz

**Çözüm:** Kullanıcıya şu yanıt gider:
```
❓ İlan oluşturamadım.
Lütfen daha detaylı yazın:
- Mahkeme adı
- Şehir
- Duruşma tarihi/saati
- Ücret
```

### AI Çalışmıyor

**Kontrol:**
1. `.env` dosyasında `GEMINI_API_KEY` var mı?
2. Flask yeniden başlatıldı mı?
3. Terminal'de `✅ Gemini AI parser aktif` yazıyor mu?

**Debug:**
```powershell
python -c "from gemini_ai_parser import GeminiIlanParser; p = GeminiIlanParser(); print('OK')"
```

---

## 📊 API Limitler

### Gemini 2.0 Flash (Ücretsiz)
- **Günlük:** 1,500 istek
- **Dakikalık:** 15 istek
- **Maliyet:** Ücretsiz

### Gemini 1.5 Pro
- **Günlük:** 50 istek (ücretsiz)
- **1 milyon token:** $3.50 (ücretli)

**Günlük kullanım tahmini:**
- 100 avukat × 2 ilan/gün = 200 istek ✅ Ücretsiz limit içinde

---

## 🚀 Gelecek Geliştirmeler

- [ ] Kategori otomatik tespiti (Ceza, Aile, Ticaret...)
- [ ] Duruşma tarih/saat parse
- [ ] Aciliyet tespiti (yarın, bugün, acil...)
- [ ] Mahkeme adres doğrulama
- [ ] Çoklu ilan tek mesajda (örn: "3 duruşmam var...")

---

## 📞 Destek

Sorularınız için:
- 📧 Email: destek@utap.com.tr
- 💬 WhatsApp: Bot'a #YARDIM yazın
- 🌐 Dokümantasyon: docs/

---

**Hazırladı:** GitHub Copilot  
**Tarih:** 22 Ocak 2025  
**Versiyon:** 1.0  
