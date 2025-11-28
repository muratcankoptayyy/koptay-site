# ULUSAL TEVKİL AĞI PROJESİ

## 🎯 Proje Hakkında
Avukatların duruşma temsili, tevkil ve görev devri yapabildiği **merkezi WhatsApp bot** destekli platform.

**Öne Çıkan Özellik:** Tek WhatsApp numarası üzerinden tüm avukatlar için otomatik ilan oluşturma ve bildirim sistemi!

---

## 🚀 Hızlı Kurulum

### 1. Projeyi İndirin
```bash
git clone https://github.com/your-repo/tevkil-proje.git
cd tevkil-proje
```

### 2. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 3. Veritabanını Oluşturun
```bash
python setup_db.py
```

### 4. **WhatsApp Credentials Ekleyin** ⭐ ÖNEMLİ

**Otomatik (Önerilen):**
```bash
python setup_whatsapp.py
```

**Manuel:**
```bash
copy .env.example .env
# .env dosyasını düzenleyin ve Meta credentials'larınızı ekleyin
```

📚 **Detaylı rehber:** `CREDENTIALS_NASIL_ALINIR.md`

### 5. Uygulamayı Başlatın
```bash
python app.py
```

🌐 **Tarayıcıda açın:** http://127.0.0.1:5000

---

## 📱 Özellikler

### ✅ Temel Özellikler
- Duruşma temsili ilan oluşturma
- İlanlara başvurma sistemi
- Kullanıcı profilleri ve değerlendirmeler
- 81 il, 595 adliye verisi
- Gerçek zamanlı bildirimler
- Arama ve filtreleme

### ⭐ WhatsApp Entegrasyonu (Merkezi Bot)
- **TEK NUMARA** - Tüm avukatlar için WhatsApp hizmeti
- **#ILAN komutu** - WhatsApp'tan hızlı ilan oluşturma
- **Otomatik bildirimler** - Yeni başvuru, kabul, red
- **Akıllı komutlar** - #YARDIM, #DURUM, #ILANLARIM
- **Telefon doğrulama** - Kullanıcı otomatik tanınır

---

## 📋 WhatsApp Komutları

| Komut | İşlev |
|-------|-------|
| `#ILAN` | Yeni ilan oluştur |
| `#YARDIM` | Yardım menüsü |
| `#DURUM` | Hesap durumunu gör |
| `#ILANLARIM` | Aktif ilanlarımı listele |
| `#BASVURULARIM` | Başvurularımı göster |

**Örnek kullanım:**
```
#ILAN
Başlık: Ankara Adliyesi Duruşma Temsili
Kategori: Ceza Hukuku
Şehir: Ankara
Açıklama: 25 Ocak saat 14:00 duruşma
Fiyat: 3500
Aciliyet: Acil
```

---

## 🛠️ Teknolojiler

**Backend:**
- Flask (Python web framework)
- SQLAlchemy (ORM)
- Flask-Login (Authentication)
- Meta WhatsApp Cloud API

**Frontend:**
- HTML5 / CSS3
- Tailwind CSS
- Alpine.js
- Chart.js

**Database:**
- SQLite (development)
- PostgreSQL (production)

**Deployment:**
- Railway.app / Render.com
- Ngrok (local test)

---

## 📚 Dokümantasyon

### Başlangıç Rehberleri
- 📖 **[Credentials Nasıl Alınır](CREDENTIALS_NASIL_ALINIR.md)** - En basit anlatım
- 🚀 **[Hızlı Başlangıç](WHATSAPP_HIZLI_BASLANGIC.md)** - 3 dakikada kurulum
- 📋 **[Detaylı Kurulum](WHATSAPP_KURULUM.md)** - Adım adım ekran görüntülü

### Teknik Dökümanlar
- `app.py` - Ana Flask uygulaması
- `whatsapp_central_bot.py` - Merkezi WhatsApp bot
- `whatsapp_meta_api.py` - Meta API wrapper
- `models.py` - Database modelleri

---

## 🧪 Test Etme

### Web Arayüzü ile Test
```
http://127.0.0.1:5000/whatsapp/setup
```

### Script ile Test
```bash
python setup_whatsapp.py test
```

### Gerçek WhatsApp ile Test
1. Profilinize telefon numaranızı ekleyin
2. Meta'da test numarası olarak kaydedin
3. Meta WhatsApp numarasına `#YARDIM` gönderin

---

## 🔑 .env Dosyası Örneği

```env
# Flask
FLASK_SECRET_KEY=dev-secret-key-2025

# Database
DATABASE_URL=sqlite:///tevkil.db

# Meta WhatsApp API
META_PHONE_NUMBER_ID=123456789012345
META_ACCESS_TOKEN=EAAxxxxxxxxxxxxx...
META_WEBHOOK_VERIFY_TOKEN=tevkil_webhook_2025
```

**NOT:** Gerçek credentials için `python setup_whatsapp.py` çalıştırın

---

## 📁 Proje Yapısı

```
tevkil_proje/
├── app.py                          # Ana Flask uygulaması
├── models.py                       # Database modelleri
├── whatsapp_central_bot.py         # Merkezi WhatsApp bot
├── whatsapp_meta_api.py            # Meta API wrapper
├── setup_whatsapp.py               # Otomatik kurulum script
├── templates/                      # HTML şablonları
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── whatsapp_setup.html
│   └── ...
├── static/                         # CSS, JS, resimler
│   └── logo.svg
├── instance/                       # SQLite veritabanı
│   └── tevkil.db
├── .env                           # Environment variables
├── .env.example                   # Örnek env dosyası
├── requirements.txt               # Python bağımlılıkları
└── README.md                      # Bu dosya
```

---

## ❗ Sık Sorulan Sorular

### WhatsApp için Meta hesabı gerekli mi?
Evet, ancak tamamen ücretsiz! Detaylı rehber: `CREDENTIALS_NASIL_ALINIR.md`

### Test numarası limiti var mı?
Evet, Meta'da 5 test numarası ekleyebilirsiniz (ücretsiz).

### Production'da nasıl kullanılır?
1. Kalıcı Access Token alın
2. Domain adınızı Meta'ya webhook olarak kaydedin
3. HTTPS kullanın

### Local test için ngrok şart mı?
Evet, Meta webhook'ları için public URL gerekir. Ngrok ücretsiz!

---

## 🔒 Güvenlik

- ⚠️ `.env` dosyasını ASLA GitHub'a yüklemeyin
- ⚠️ `.gitignore`'da `.env` olduğundan emin olun
- ⚠️ Production'da güçlü SECRET_KEY kullanın
- ⚠️ Access Token'ları güvenli saklayın

---

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing`)
5. Pull Request açın

---

## 📞 Destek

- 📧 E-posta: destek@utap.com.tr
- 🌐 Website: https://utap.com.tr
- 📚 Dokümantasyon: `WHATSAPP_KURULUM.md`

---

## 📝 Lisans
MIT License - Özgürce kullanabilirsiniz!

---

## 👨‍💻 Geliştirme Ekibi
**Ulusal Tevkil Ağı Projesi** - 2025

**Özel Teşekkürler:**
- Meta WhatsApp Cloud API
- Flask Community
- Tailwind CSS

---

## 🎉 Başlangıç Checklist

- [ ] Projeyi indirdim
- [ ] Bağımlılıkları yükledim
- [ ] Veritabanını oluşturdum
- [ ] `CREDENTIALS_NASIL_ALINIR.md` okudum
- [ ] Meta Developer hesabı açtım
- [ ] WhatsApp credentials aldım
- [ ] `.env` dosyasını oluşturdum
- [ ] `python app.py` ile başlattım
- [ ] Web arayüzünde test ettim
- [ ] WhatsApp'tan `#YARDIM` gönderdim

**Hepsi tamamsa: Hazırsınız! 🚀**

---

**İyi çalışmalar!** 💼⚖️
