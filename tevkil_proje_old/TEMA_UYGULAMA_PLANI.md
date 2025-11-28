# 🎨 Minimal White Tema - Tam Uygulama Planı

## 📋 Strateji

### Faz 1: Core CSS Global Değişiklikler (ÖNCELİK)
- [x] base.html - CSS framework ve global stiller
- [ ] Toplu değiştir komutları ile tüm dosyalarda:
  - `rounded-lg` → `` (sil)
  - `rounded-md` → `` (sil)
  - `shadow-md` → `` (sil)
  - `shadow-lg` → `` (sil)
  - `bg-blue-500` → `bg-gray-900`
  - `bg-blue-600` → `bg-gray-900`
  - `border-gray-100` → `border-gray-300`
  - `border-gray-200` → `border-gray-300`

### Faz 2: Kritik Sayfalar (Kullanıcı Akışı)
1. **index.html** - Ana sayfa
2. **register.html** - Kayıt
3. **login.html** - Giriş
4. **dashboard.html** - Dashboard
5. **posts_list.html** - İlan listesi
6. **post_detail.html** - İlan detay
7. **post_create.html** - İlan oluştur
8. **messages.html** - Mesajlaşma
9. **profile.html** - Profil
10. **settings.html** - Ayarlar

### Faz 3: Diğer Sayfalar
- Admin sayfaları
- 2FA sayfaları
- Email templates (düşük öncelik)

## 🎯 Minimal White Tema Kuralları

### Değiştirilecekler:
```
❌ rounded-* → Kaldır (keskin köşeler)
❌ shadow-* → Kaldır (flat design)
❌ bg-gradient-* → bg-white veya bg-gray-900
❌ bg-blue-* → bg-gray-900
❌ text-blue-* → text-gray-900
❌ border-gray-100/200 → border-gray-300
❌ font-bold → font-medium veya font-light
```

### Kullanılacaklar:
```
✅ border-gray-300 (ana çerçeveler)
✅ border-gray-200 (ince ayırıcılar)
✅ bg-gray-900 (butonlar, aktif menü)
✅ text-gray-900 (başlıklar)
✅ text-gray-600 (normal metin)
✅ text-gray-400 (ikincil metin)
✅ font-light (300)
✅ font-medium (500)
✅ hover:border-gray-900
```

## 📊 İlerleme
- [x] Faz 1: CSS Global - %100
- [ ] Faz 2: Kritik Sayfalar - %0
- [ ] Faz 3: Diğer Sayfalar - %0
