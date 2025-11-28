# 🎯 İki Aşamalı Onay Sistemi - Kullanıcı Kılavuzu

## ✅ Yeni Özellik: AI Önizleme + Onay

Artık AI doğrudan ilan oluşturmaz! Önce size önizleme gösterir, siz onaylarsanız yayınlanır.

---

## 📱 Nasıl Çalışır?

### Adım 1: Mesajınızı Gönderin
```
Ankara 4. Asliye Ceza Mahkemesi'nde saat 10:00 duruşmam var,
tevkil arıyorum, ücret 2000 TL
```

### Adım 2: AI Analiz Eder
```
🤖 AI İLAN ÖNİZLEME

AI mesajınızı analiz etti. Lütfen kontrol edin:

━━━━━━━━━━━━━━━━━━━━━━━━━
📋 BAŞLIK
Ceza Davası Tevkili

🏛️ MAHKEME
Ankara 4. Asliye Ceza Mahkemesi

📍 ŞEHİR
Ankara

📂 KATEGORİ
Ceza Hukuku

📝 AÇIKLAMA
Saat 10:00 duruşma için tevkil arıyorum.

💰 ÜCRET
2000 TL

⚡ ACİLİYET
Normal
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Bilgiler doğru mu?

👍 ONAYLAMAK İÇİN:
#ONAYLA

❌ İPTAL ETMEK İÇİN:
#IPTAL

💡 Not: Onayladıktan sonra web sitesinden düzenleyebilirsiniz.
```

### Adım 3a: Onaylayın
```
#ONAYLA
```

**Yanıt:**
```
✅ İLAN YAYINLANDI!

📋 Ceza Davası Tevkili
🏛️ Ankara 4. Asliye Ceza Mahkemesi
📍 Ankara
📂 Ceza Hukuku
💰 2000 TL
⚡ Normal

🔗 https://utap.com.tr/posts/123

✅ İlanınız aktif! Başvurular gelmeye başlayacak.
```

### Adım 3b: İptal Edin
```
#IPTAL
```

**Yanıt:**
```
❌ İlan iptal edildi.

Yeni ilan oluşturmak için mesajınızı gönderin.
```

---

## 🔍 AI'nin Otomatik Tespit Ettiği Bilgiler

### 1. Kategori (Otomatik)
AI mahkeme adından ve mesajdan kategoriyi tespit eder:

| Anahtar Kelime | Kategori |
|----------------|----------|
| Aile Mahkemesi, boşanma | Aile Hukuku |
| Ceza Mahkemesi, Ağır Ceza | Ceza Hukuku |
| Ticaret Mahkemesi | Ticaret Hukuku |
| İcra Müdürlüğü, icra | İcra ve İflas |
| İş Mahkemesi | İş Hukuku |
| İdare Mahkemesi | İdare Hukuku |
| Diğer | Genel Hukuk |

### 2. Aciliyet (Otomatik)
AI mesajınızdan aciliyeti anlar:

| Kelimeler | Aciliyet |
|-----------|----------|
| "acil", "hemen", "bugün" | Acil |
| "çok acil" | Çok Acil |
| "yarın", belirtilmemiş | Normal |

### 3. Diğer Bilgiler
- **Başlık:** AI kısa ve öz başlık oluşturur
- **Şehir:** Mahkeme adından çıkarır
- **Mahkeme:** Tam mahkeme adı
- **Açıklama:** Mesajınızı düzenler
- **Ücret:** Sayısal değeri bulur (yoksa 0)

---

## 💡 Örnek Senaryolar

### Örnek 1: Basit Duruşma
**Mesaj:**
```
İstanbul 5. Aile Mahkemesi'nde yarın saat 10:00 duruşmam var, 3000 TL
```

**AI Önizlemesi:**
```
📋 Aile Mahkemesi Duruşma Temsili
🏛️ İstanbul 5. Aile Mahkemesi
📍 İstanbul
📂 Aile Hukuku
💰 3000 TL
⚡ Normal
```

### Örnek 2: Acil Duruşma
**Mesaj:**
```
Ankara 2. Ağır Ceza'da bugün öğleden sonra acil duruşma var, 5000 TL
```

**AI Önizlemesi:**
```
📋 Acil Ceza Davası Temsili
🏛️ Ankara 2. Ağır Ceza Mahkemesi
📍 Ankara
📂 Ceza Hukuku
💰 5000 TL
⚡ Acil
```

### Örnek 3: İcra Takibi
**Mesaj:**
```
Kadıköy İcra Müdürlüğü'nde dosya takibi yapacak meslektaş lazım, 2500 TL ücret
```

**AI Önizlemesi:**
```
📋 İcra Dosya Takibi
🏛️ Kadıköy İcra Müdürlüğü
📍 İstanbul
📂 İcra ve İflas
💰 2500 TL
⚡ Normal
```

---

## ⏰ Zaman Aşımı

Önizleme **15 dakika** geçerlidir. Süre dolarsa:

```
⏰ Onay süresi doldu.

Lütfen ilanınızı yeniden gönderin.
```

---

## 🛠️ Sorun Giderme

### Soru: "AI mesajımı anlamadı"
**Çözüm:** Daha detaylı yazın:
- ✅ Mahkeme adı
- ✅ Şehir (mahkeme adında yoksa)
- ✅ Duruşma saati/tarihi
- ✅ Ücret

**İyi Örnek:**
```
Ankara 4. Asliye Ceza Mahkemesi'nde 
saat 10:00 duruşma, 2000 TL
```

**Kötü Örnek:**
```
yarın duruşma var
```

### Soru: "Onay bekleyen ilanım kayboldu"
**Sebep:** 15 dakika geçmiş olabilir.

**Çözüm:** Mesajınızı yeniden gönderin.

### Soru: "Kategori yanlış seçildi"
**Çözüm:** 
1. #IPTAL yazın
2. Mesajınızda kategori belirtin:
```
Ankara 4. Asliye Ceza - Ceza davası, saat 10:00, 2000 TL
```

### Soru: "#ONAYLA yazınca hata veriyor"
**Kontrol:**
1. Önce AI önizlemesi aldınız mı?
2. 15 dakika geçti mi?
3. Başka telefon numarasından mı yazıyorsunuz?

---

## 🎯 Avantajları

### ✅ Önceki Sistem (Otomatik)
- ❌ AI yanlış anlayabilir
- ❌ Kontrol edemezsiniz
- ❌ Hata olursa düzeltmek zor

### ✅ Yeni Sistem (Onaylı)
- ✅ Yayınlanmadan önce görürsünüz
- ✅ Hataları fark edersiniz
- ✅ İstediğiniz zaman iptal edebilirsiniz
- ✅ Web'den düzenleme imkanı

---

## 📋 Komut Özeti

| Komut | Açıklama |
|-------|----------|
| Doğal mesaj | AI analiz eder, önizleme gösterir |
| #ONAYLA | AI ilanını yayınla |
| #IPTAL | AI ilanını iptal et |
| #ILAN | Manuel şablonlu ilan |
| #ILANLARIM | Aktif ilanlarımı göster |
| #YARDIM | Yardım menüsü |

---

## 🚀 Hızlı Başlangıç

1. **Mesajınızı yazın:**
   ```
   Ankara 4. Asliye Ceza'da saat 10:00 duruşma, 2000 TL
   ```

2. **AI önizlemesini kontrol edin**

3. **Onaylayın:**
   ```
   #ONAYLA
   ```

4. **İlanınız yayında! 🎉**

---

**Hazırladı:** GitHub Copilot  
**Tarih:** 22 Ocak 2025  
**Versiyon:** 2.0 (İki Aşamalı Onay)
