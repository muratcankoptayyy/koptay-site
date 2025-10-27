# 🧩 BILEŞEN KÜTÜPHANESİ

Minimal White Tema için hazır HTML kod parçaları.

---

## 📊 İSTATİSTİK KARTLARI

### Basit Stats Card
```html
<div class="p-12 border border-gray-300">
    <div class="text-5xl font-light text-gray-900 mb-2">1,234+</div>
    <div class="text-sm text-gray-400 uppercase tracking-wider">Kayıtlı Avukat</div>
</div>
```

### Stats Card (Değişim İle)
```html
<div class="p-8">
    <div class="text-5xl font-light text-gray-900 mb-2">150</div>
    <div class="text-sm text-gray-400 uppercase tracking-wider">Toplam İlan</div>
    <div class="text-xs text-gray-400 mt-4">+12% ↑</div>
</div>
```

### 4'lü Stats Grid
```html
<div class="grid grid-cols-4 gap-8">
    <div class="p-8">
        <div class="text-5xl font-light text-gray-900 mb-2">150</div>
        <div class="text-sm text-gray-400 uppercase tracking-wider">Toplam İlan</div>
    </div>
    <div class="p-8">
        <div class="text-5xl font-light text-gray-900 mb-2">53</div>
        <div class="text-sm text-gray-400 uppercase tracking-wider">Başvurular</div>
    </div>
    <div class="p-8">
        <div class="text-5xl font-light text-gray-900 mb-2">44</div>
        <div class="text-sm text-gray-400 uppercase tracking-wider">Mesajlar</div>
    </div>
    <div class="p-8">
        <div class="text-5xl font-light text-gray-900 mb-2">127</div>
        <div class="text-sm text-gray-400 uppercase tracking-wider">Tamamlanan</div>
    </div>
</div>
```

---

## 📝 İLAN/POST KARTLARI

### İlan Kartı (Tam)
```html
<div class="border border-gray-300 p-8 hover:border-gray-900 transition-colors">
    <div class="flex justify-between items-start mb-4">
        <div>
            <h3 class="text-xl font-light text-gray-900 mb-2">Boşanma Davası - İstanbul</h3>
            <div class="flex gap-4 text-sm text-gray-400">
                <span>Kategori: Boşanma</span>
                <span>•</span>
                <span>Şehir: İstanbul</span>
                <span>•</span>
                <span>Durum: Aktif</span>
            </div>
        </div>
        <div class="text-right">
            <div class="text-2xl font-light text-gray-900">₺5,000</div>
            <div class="text-xs text-gray-400 mt-1">Ücret</div>
        </div>
    </div>
    
    <p class="text-gray-600 mb-6 font-light leading-relaxed">
        Çekişmeli boşanma davası için deneyimli avukat aranmaktadır...
    </p>
    
    <div class="flex justify-between items-center">
        <div class="text-sm text-gray-400">
            12 başvuru • 2 gün önce yayınlandı
        </div>
        <a href="#" class="px-8 py-3 bg-gray-900 text-white text-sm hover:bg-gray-800">
            Detayları Gör
        </a>
    </div>
</div>
```

### İlan Kartı (Basit)
```html
<div class="border border-gray-300 p-8 hover:border-gray-900">
    <h3 class="text-xl font-light text-gray-900 mb-3">İlan Başlığı</h3>
    <p class="text-gray-600 font-light mb-4">Kısa açıklama buraya...</p>
    <button class="px-8 py-3 bg-gray-900 text-white">Detay</button>
</div>
```

---

## 🔘 BUTONLAR

### Primary Button
```html
<button class="px-8 py-3 bg-gray-900 text-white hover:bg-gray-800">
    Gönder
</button>
```

### Secondary Button
```html
<button class="px-8 py-3 border border-gray-300 text-gray-900 hover:border-gray-900">
    İptal
</button>
```

### Link Button
```html
<a href="#" class="text-gray-900 hover:underline">
    Daha Fazla Gör →
</a>
```

### Button Group
```html
<div class="flex gap-4">
    <button class="px-8 py-3 bg-gray-900 text-white hover:bg-gray-800">
        Kaydet
    </button>
    <button class="px-8 py-3 border border-gray-300 text-gray-900 hover:border-gray-900">
        İptal
    </button>
</div>
```

---

## 📥 FORM ELEMENTLERİ

### Text Input
```html
<div class="mb-6">
    <label class="block text-sm text-gray-500 mb-2">E-posta</label>
    <input type="email" 
           class="w-full px-0 py-3 border-0 border-b border-gray-200 
                  focus:border-gray-900 focus:outline-none font-light"
           placeholder="ornek@email.com">
</div>
```

### Select Dropdown
```html
<div class="mb-6">
    <label class="block text-sm text-gray-500 mb-2">Kategori</label>
    <select class="w-full px-0 py-3 border-0 border-b border-gray-200 
                   focus:border-gray-900 focus:outline-none font-light bg-white">
        <option>Boşanma</option>
        <option>İcra</option>
        <option>Ceza</option>
    </select>
</div>
```

### Textarea
```html
<div class="mb-6">
    <label class="block text-sm text-gray-500 mb-2">Açıklama</label>
    <textarea rows="4" 
              class="w-full px-0 py-3 border-0 border-b border-gray-200 
                     focus:border-gray-900 focus:outline-none font-light resize-none"></textarea>
</div>
```

### Checkbox
```html
<label class="flex items-center gap-3 cursor-pointer">
    <input type="checkbox" class="w-4 h-4">
    <span class="text-gray-700">Beni hatırla</span>
</label>
```

### Toggle Switch
```html
<label class="relative inline-flex items-center cursor-pointer">
    <input type="checkbox" checked class="sr-only peer">
    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-checked:bg-gray-900 
                peer-checked:after:translate-x-full peer-checked:after:border-white 
                after:content-[''] after:absolute after:top-[2px] after:left-[2px] 
                after:bg-white after:border-gray-300 after:border after:h-5 after:w-5 
                after:transition-all"></div>
</label>
```

### İki Sütun Form
```html
<div class="grid grid-cols-2 gap-8">
    <div>
        <label class="block text-sm text-gray-500 mb-2">Ad</label>
        <input type="text" 
               class="w-full px-0 py-3 border-0 border-b border-gray-200 
                      focus:border-gray-900 focus:outline-none font-light">
    </div>
    <div>
        <label class="block text-sm text-gray-500 mb-2">Soyad</label>
        <input type="text" 
               class="w-full px-0 py-3 border-0 border-b border-gray-200 
                      focus:border-gray-900 focus:outline-none font-light">
    </div>
</div>
```

---

## 💬 MESAJLAŞMA BİLEŞENLERİ

### Gönderilen Mesaj
```html
<div class="flex items-start gap-4 justify-end">
    <div>
        <div class="bg-gray-900 text-white px-6 py-4 max-w-lg">
            <p class="font-light">Merhaba, nasılsınız?</p>
        </div>
        <div class="text-right">
            <span class="text-xs text-gray-400 mt-2 inline-block">10:26</span>
        </div>
    </div>
    <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-gray-700 text-xs">
        MK
    </div>
</div>
```

### Alınan Mesaj
```html
<div class="flex items-start gap-4">
    <div class="w-8 h-8 bg-gray-900 rounded-full flex items-center justify-center text-white text-xs">
        AK
    </div>
    <div>
        <div class="bg-gray-100 px-6 py-4 max-w-lg">
            <p class="text-gray-900 font-light">İyiyim, teşekkürler!</p>
        </div>
        <span class="text-xs text-gray-400 mt-2 inline-block">10:24</span>
    </div>
</div>
```

### Konuşma Listesi Item
```html
<div class="p-6 border-b border-gray-200 hover:bg-gray-50 cursor-pointer">
    <div class="flex items-start gap-4">
        <div class="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center text-white flex-shrink-0">
            AK
        </div>
        <div class="flex-1 min-w-0">
            <div class="flex justify-between items-start mb-1">
                <h3 class="font-medium text-gray-900">Av. Ahmet Kaya</h3>
                <span class="text-xs text-gray-400">10 dk</span>
            </div>
            <p class="text-sm text-gray-600 truncate">Son mesaj içeriği...</p>
            <div class="mt-2">
                <span class="bg-gray-900 text-white text-xs px-2 py-1">2</span>
            </div>
        </div>
    </div>
</div>
```

---

## 📅 TİMELİNE / AKTİVİTE

### Timeline Item
```html
<div class="flex items-start gap-6 pb-6 border-b border-gray-200">
    <div class="text-xs text-gray-400 w-16">2 saat</div>
    <div class="flex-1">
        <div class="font-medium text-gray-900">Yeni ilan oluşturuldu</div>
        <div class="text-sm text-gray-500 mt-1">Boşanma davası - İstanbul Adliyesi</div>
    </div>
</div>
```

### Timeline (Tam Liste)
```html
<div class="space-y-6">
    <div class="flex items-start gap-6 pb-6 border-b border-gray-200">
        <div class="text-xs text-gray-400 w-16">2 saat</div>
        <div class="flex-1">
            <div class="font-medium text-gray-900">Yeni ilan oluşturuldu</div>
            <div class="text-sm text-gray-500 mt-1">Boşanma davası</div>
        </div>
    </div>
    <div class="flex items-start gap-6 pb-6 border-b border-gray-200">
        <div class="text-xs text-gray-400 w-16">5 saat</div>
        <div class="flex-1">
            <div class="font-medium text-gray-900">Yeni başvuru alındı</div>
            <div class="text-sm text-gray-500 mt-1">Av. Mehmet Yılmaz başvurdu</div>
        </div>
    </div>
</div>
```

---

## 🏷️ ETIKETLER & BADGE

### Tag
```html
<span class="px-4 py-2 bg-gray-100 text-gray-900 text-sm">
    Aile Hukuku
</span>
```

### Tag Group
```html
<div class="flex flex-wrap gap-3">
    <span class="px-4 py-2 bg-gray-100 text-gray-900 text-sm">Aile Hukuku</span>
    <span class="px-4 py-2 bg-gray-100 text-gray-900 text-sm">İcra-İflas</span>
    <span class="px-4 py-2 bg-gray-100 text-gray-900 text-sm">Ticaret</span>
</div>
```

### Notification Badge
```html
<span class="bg-gray-900 text-white text-xs px-2 py-1">3</span>
```

### Status Badge
```html
<span class="px-3 py-1 text-xs bg-gray-100 text-gray-700">Aktif</span>
```

---

## 🧭 NAVİGASYON

### Top Bar
```html
<div class="fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-300 z-20 flex items-center px-12">
    <h1 class="text-xl font-light text-gray-900">Tevkil</h1>
    <div class="ml-auto flex items-center gap-8">
        <button class="text-gray-400 hover:text-gray-900">🔍</button>
        <button class="text-gray-400 hover:text-gray-900 relative">
            🔔
            <span class="absolute -top-1 -right-1 bg-black text-white text-xs w-4 h-4 rounded-full flex items-center justify-center">3</span>
        </button>
        <div class="w-8 h-8 bg-gray-900 rounded-full flex items-center justify-center text-white text-sm font-light">
            MK
        </div>
    </div>
</div>
```

### Sidebar
```html
<div class="fixed left-0 top-16 h-full w-48 bg-white border-r border-gray-300 z-10">
    <nav class="px-6 py-12">
        <a href="#" class="flex items-center gap-4 py-4 text-gray-900 font-medium border-l-2 border-gray-900 pl-4 -ml-6">
            <span>Dashboard</span>
        </a>
        <a href="#" class="flex items-center gap-4 py-4 text-gray-400 hover:text-gray-900 border-l-2 border-transparent pl-4 -ml-6">
            <span>İlanlar</span>
        </a>
        <a href="#" class="flex items-center gap-4 py-4 text-gray-400 hover:text-gray-900 border-l-2 border-transparent pl-4 -ml-6">
            <span>Sohbetler</span>
        </a>
    </nav>
</div>
```

### Tab Navigation
```html
<div class="flex gap-4 mb-12">
    <button class="px-6 py-2 bg-gray-900 text-white text-sm">Tümü</button>
    <button class="px-6 py-2 border border-gray-200 text-gray-600 text-sm hover:border-gray-900">Aktif</button>
    <button class="px-6 py-2 border border-gray-200 text-gray-600 text-sm hover:border-gray-900">Tamamlanan</button>
</div>
```

---

## 🔍 ARAMA & FİLTRELEME

### Arama Çubuğu
```html
<input type="text" 
       placeholder="Ara..." 
       class="w-full px-0 py-3 border-0 border-b border-gray-200 
              focus:border-gray-900 focus:outline-none font-light">
```

### Filtre Bar
```html
<div class="flex gap-6 mb-8">
    <input type="text" 
           placeholder="İlan ara..." 
           class="flex-1 px-0 py-3 border-0 border-b border-gray-200 
                  focus:border-gray-900 focus:outline-none font-light">
    
    <select class="px-0 py-3 border-0 border-b border-gray-200 
                   focus:border-gray-900 focus:outline-none font-light bg-white">
        <option>Tüm Kategoriler</option>
        <option>Boşanma</option>
        <option>İcra</option>
    </select>

    <select class="px-0 py-3 border-0 border-b border-gray-200 
                   focus:border-gray-900 focus:outline-none font-light bg-white">
        <option>Tüm Şehirler</option>
        <option>İstanbul</option>
        <option>Ankara</option>
    </select>
</div>
```

---

## 📑 PAGİNATİON

### Sayfa Numaraları
```html
<div class="flex justify-center gap-4">
    <button class="w-10 h-10 border border-gray-200 hover:border-gray-900">1</button>
    <button class="w-10 h-10 bg-gray-900 text-white">2</button>
    <button class="w-10 h-10 border border-gray-200 hover:border-gray-900">3</button>
    <button class="w-10 h-10 border border-gray-200 hover:border-gray-900">→</button>
</div>
```

---

## ⚙️ AYARLAR

### Ayar Satırı (Toggle ile)
```html
<div class="flex items-center justify-between py-4 border-t border-gray-200">
    <div>
        <h4 class="font-medium text-gray-900">Bildirimler</h4>
        <p class="text-sm text-gray-500">E-posta bildirimleri al</p>
    </div>
    <label class="relative inline-flex items-center cursor-pointer">
        <input type="checkbox" checked class="sr-only peer">
        <div class="w-11 h-6 bg-gray-200 peer-checked:bg-gray-900 
                    peer-checked:after:translate-x-full after:absolute 
                    after:top-[2px] after:left-[2px] after:bg-white 
                    after:h-5 after:w-5 after:transition-all"></div>
    </label>
</div>
```

---

## 📦 BÖLÜM AYIRICI

### Başlıklı Bölüm
```html
<div class="mb-16 pb-16 border-b border-gray-300">
    <h3 class="text-2xl font-light text-gray-900 mb-8">Başlık</h3>
    <!-- İçerik buraya -->
</div>
```

---

## 🎯 KULLANIM ÖRNEKLERİ

### Flask ile Stats
```html
<div class="grid grid-cols-4 gap-8">
    <div class="p-8">
        <div class="text-5xl font-light text-gray-900 mb-2">{{ total_posts }}</div>
        <div class="text-sm text-gray-400 uppercase tracking-wider">Toplam İlan</div>
    </div>
</div>
```

### Flask ile İlan Listesi
```html
{% for post in posts %}
<div class="border border-gray-300 p-8 hover:border-gray-900">
    <h3 class="text-xl font-light text-gray-900 mb-2">{{ post.title }}</h3>
    <p class="text-gray-600 font-light mb-4">{{ post.description }}</p>
    <a href="{{ url_for('post_detail', id=post.id) }}" 
       class="px-8 py-3 bg-gray-900 text-white inline-block">Detay</a>
</div>
{% endfor %}
```

---

**Tüm bileşenler copy-paste ile kullanıma hazır! 🚀**
