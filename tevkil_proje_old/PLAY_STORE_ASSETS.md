# Play Store Grafik Asset'leri Hazırlama Rehberi

## 📱 GEREKLİ GÖRSEL ASSET'LER

### 1. Hi-Res Icon (512x512 PNG) ✅
**Durum:** Logo zaten var (`static/logo-icon.svg`)

**Manuel Export (Tarayıcıda):**
1. https://tevkil.fly.dev/static/logo-icon.svg adresini açın
2. Sağ tık → "Farklı kaydet" → SVG olarak kaydedin
3. https://www.iloveimg.com/resize-image/resize-svg adresine gidin
4. SVG'yi yükleyin
5. Boyut: 512x512 px, PNG formatı
6. İndir → `hi-res-icon-512x512.png` olarak kaydedin

**Alternatif (Figma/Canva):**
- Logo'yu import edin
- Export: 512x512 PNG, transparent background
- Play Console'a yükleyin

---

### 2. Feature Graphic (1024x500 JPEG/PNG) ❌
**Durum:** Oluşturulmalı

**Canva Template (Önerilen):**
1. https://www.canva.com adresine gidin
2. "Custom size" → 1024 x 500 px
3. Tasarım önerileri:
   - Sol tarafta uygulama ekran görüntüsü mockup
   - Sağ tarafta metin: "Tevkil - Avukatlar Arası Güvenli Ağ"
   - Alt kısımda tagline: "Duruşma Temsili | Hızlı | Güvenli"
   - Renk paleti: #1661da (primary blue), beyaz, gri
4. Export: PNG veya JPEG
5. Dosya adı: `feature-graphic-1024x500.png`

**Hızlı Template (opsiyonel, ben hazırlayabilirim):**
```
+--------------------------------------------------+
|                                                  |
|  [Logo]  TEVKİL                                  |
|                                                  |
|  Türkiye'nin İlk Avukat Tevkil Platformu        |
|                                                  |
|  ✓ Güvenli  ✓ Hızlı  ✓ Profesyonel             |
|                                                  |
+--------------------------------------------------+
```

---

### 3. Telefon Ekran Görüntüleri (Min 2, Maks 8) ❌
**Durum:** Oluşturulmalı

**Gereksinimler:**
- Format: PNG veya JPEG
- Aspect ratio: 16:9 veya 9:16
- Boyut: Min 320px, Max 3840px
- Önerilen: 1080x1920 (9:16 portrait)

**Hangi Ekranlar? (Önerilen Sıralama):**
1. **Ana Sayfa / Landing** - "Hoş geldiniz" ekranı
2. **İlan Listesi** - İlanların listelendiği sayfa
3. **İlan Detay** - Tek bir ilanın detayı
4. **Chat / Mesajlaşma** - Mesajlaşma ekranı
5. **Profil** - Kullanıcı profil sayfası
6. **Harita Görünümü** - İlanların haritada gösterimi
7. **Dashboard** - İstatistikler ve özetler
8. **Bildirimler** - Bildirim listesi (opsiyonel)

**Nasıl Çekilir?**
1. Android cihazda uygulamayı açın
2. İlgili sayfaya gidin
3. Power + Volume Down tuşlarına aynı anda basın
4. Screenshot'lar Gallery/Photos'ta kaydedilir
5. Bilgisayara aktarın
6. (Opsiyonel) Frame ekleyin: https://www.screely.com veya https://mockuphone.com

**Frame Template (Opsiyonel):**
- Android cihaz frame'i eklemek için mockup araçları kullanabilirsiniz
- Ör: https://smartmockups.com/mockup-categories/device-mockups

---

### 4. Tablet Ekran Görüntüleri (Opsiyonel) ⚪
**Durum:** Opsiyonel (telefon screenshot'ları yeterli)

---

### 5. Promo Video (Opsiyonel) ⚪
**Durum:** Opsiyonel (ilk sürüm için gerekli değil)

---

## 🎨 HIZLI BAŞLANGIÇ (ADIM ADIM)

### ADIM 1: Hi-Res Icon (5 dk)
```powershell
# Tarayıcıda logo-icon.svg'yi açıp PNG olarak export edin
# Boyut: 512x512 px
# Dosya: hi-res-icon-512x512.png
```

### ADIM 2: Feature Graphic (15 dk)
**Manuel (Canva):**
1. Canva'ya giriş yapın
2. Template: 1024x500 px
3. Logo + metin ekleyin
4. Export: PNG
5. Dosya: feature-graphic-1024x500.png

**Otomatik (benden iste):**
- Logo ve metin bilgilerini kullanarak ben oluşturabilirim

### ADIM 3: Screenshot'lar (30 dk)
1. Uygulamayı Android'de açın
2. 6-8 farklı ekrandan screenshot alın
3. Bilgisayara aktarın
4. (Opsiyonel) Frame ekleyin
5. Dosya adları:
   - `screenshot-1-landing.png`
   - `screenshot-2-posts-list.png`
   - `screenshot-3-post-detail.png`
   - `screenshot-4-chat.png`
   - `screenshot-5-profile.png`
   - `screenshot-6-map.png`

---

## 📂 DOSYA YAPILANDIRMASI (Önerilen)

```
tevkil_proje/
├── play-store-assets/
│   ├── hi-res-icon-512x512.png          (512x512)
│   ├── feature-graphic-1024x500.png     (1024x500)
│   ├── screenshots/
│   │   ├── phone/
│   │   │   ├── 01-landing.png           (1080x1920)
│   │   │   ├── 02-posts-list.png        (1080x1920)
│   │   │   ├── 03-post-detail.png       (1080x1920)
│   │   │   ├── 04-chat.png              (1080x1920)
│   │   │   ├── 05-profile.png           (1080x1920)
│   │   │   └── 06-map.png               (1080x1920)
│   │   └── tablet/ (opsiyonel)
│   └── promo-video.mp4 (opsiyonel)
```

---

## 🛠️ YARDIMCI ARAÇLAR

### Grafik Tasarım:
- **Canva:** https://www.canva.com (ücretsiz)
- **Figma:** https://www.figma.com (ücretsiz)
- **Adobe Express:** https://www.adobe.com/express (ücretsiz)

### Screenshot Mockup:
- **Mockuphone:** https://mockuphone.com (ücretsiz)
- **Screely:** https://www.screely.com (ücretsiz)
- **SmartMockups:** https://smartmockups.com (ücretli ama güzel)

### SVG → PNG Converter:
- **CloudConvert:** https://cloudconvert.com/svg-to-png
- **ILoveIMG:** https://www.iloveimg.com/resize-image/resize-svg
- **Inkscape:** (desktop app, advanced)

### Boyutlandırma:
- **ILoveIMG Resize:** https://www.iloveimg.com/resize-image
- **Bulk Resize Photos:** https://bulkresizephotos.com

---

## ✅ KONTROL LİSTESİ

Play Console'a yüklemeden önce kontrol edin:

- [ ] Hi-res icon: 512x512 PNG, alpha yok ✅
- [ ] Feature graphic: 1024x500 PNG/JPEG ✅
- [ ] Phone screenshots: Min 2, max 8 ✅
- [ ] Screenshot boyutları doğru (9:16 veya 16:9) ✅
- [ ] Dosya boyutları makul (her biri <5 MB) ✅
- [ ] Görsel kalitesi yüksek (bulanık değil) ✅
- [ ] Metin okunabilir ✅
- [ ] Logo ve branding tutarlı ✅

---

## 🚀 HIZLI YÜKLEME

Play Console'da:
1. **Store presence → Main store listing**
2. **Graphics** bölümüne gidin
3. Dosyaları sürükle-bırak yapın:
   - App icon (512x512)
   - Feature graphic (1024x500)
   - Phone screenshots (en az 2)
4. **Save**

---

## ❓ SORULAR

**S: Screenshot'larda kişisel veri gösterebilir miyim?**  
C: Hayır! Test verisi veya blur kullanın.

**S: Feature graphic'te ne yazmalı?**  
C: Uygulama adı, tagline, anahtar özellikler.

**S: Screenshot kaç tane olmalı?**  
C: Minimum 2, önerilen 6-8.

**S: Tablet screenshot zorunlu mu?**  
C: Hayır, opsiyonel.

---

## 📞 YARDIM

Asset'leri hazırlamakta zorlanırsanız:
- Bana logo ve metin verin, ben template hazırlayayım
- Veya yukarıdaki araçları kullanarak kendiniz yapabilirsiniz

Herhangi bir soru için bana sorabilirsiniz! 😊
