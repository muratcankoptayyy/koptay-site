# Logo 6 (Executive Serif) Entegrasyon Rehberi

## Logo Dosyası Konumu

SVG logo kodu şu dosyada bulunmaktadır:
```
src/assets/logos/KoptayLogo6-Executive.jsx
```

## Otomatik Entegrasyon (Tamamlandı) ✅

Logo, navigasyon barına otomatik olarak eklenmiştir. Artık tüm sayfalarda görünmektedir.

### Değişiklikler:
- `src/components/Nav.jsx` dosyası güncellendi
- Logo, responsive olarak farklı ekran boyutlarına uyum sağlar
- Mobil: 48px yükseklik (h-12)
- Masaüstü: 56px yükseklik (h-14)

## Manuel Entegrasyon Seçenekleri

### 1. Başka Bir Sayfada Kullanma

Herhangi bir React bileşeninde logoyu kullanmak için:

```jsx
import KoptayLogoExecutive from '../assets/logos/KoptayLogo6-Executive'

function MyComponent() {
  return (
    <div>
      <KoptayLogoExecutive className="h-20 w-auto" />
    </div>
  )
}
```

### 2. Farklı Boyutlarda Kullanma

Logo, className prop'u ile özelleştirilebilir:

```jsx
{/* Küçük boyut */}
<KoptayLogoExecutive className="h-8 w-auto" />

{/* Orta boyut */}
<KoptayLogoExecutive className="h-16 w-auto" />

{/* Büyük boyut */}
<KoptayLogoExecutive className="h-32 w-auto" />

{/* Tam genişlik */}
<KoptayLogoExecutive className="w-full h-auto" />
```

### 3. Footer'da Kullanma

Footer bileşeninde logo eklemek için `src/components/Footer.jsx` dosyasını güncelleyin:

```jsx
import KoptayLogoExecutive from '../assets/logos/KoptayLogo6-Executive'

// Footer içinde:
<KoptayLogoExecutive className="h-16 w-auto mb-4" />
```

### 4. Ana Sayfada Hero Bölümünde Kullanma

Ana sayfa hero bölümünde büyük logo göstermek için:

```jsx
<KoptayLogoExecutive className="h-32 md:h-40 w-auto mx-auto" />
```

## Renk Özelleştirme

Logo, sitenizin mevcut renk paletini (#2D3748 ve #548c8d) kullanır. 

Renkleri değiştirmek isterseniz, `src/assets/logos/KoptayLogo6-Executive.jsx` dosyasını düzenleyin:

```jsx
// Ana metin rengi (şu an: #2D3748)
fill="#2D3748"

// İkincil renk (şu an: #548c8d)
stroke="#548c8d"
```

## Saf SVG Kodunu Alma

Eğer React bileşeni yerine saf SVG kodu isterseniz:

```svg
<svg viewBox="0 0 300 120" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
  <!-- SVG içeriği KoptayLogo6-Executive.jsx dosyasındaki return bloğundadır -->
</svg>
```

Tam SVG kodu için `src/assets/logos/KoptayLogo6-Executive.jsx` dosyasının içindeki `<svg>` etiketlerini kopyalayın.

## Dışa Aktarma Seçenekleri

### PNG Olarak Kaydetme

1. `/logo-showcase` sayfasını açın
2. Logo 6'ya sağ tıklayın
3. "Resmi farklı kaydet" seçeneğini kullanın

### PDF/Print İçin

Logo SVG olduğu için, herhangi bir boyutta yazdırılabilir:
- Kartvizit
- Antetli kağıt
- Tabelalar
- Dijital medya

## Kullanım Önerileri

### Minimum Boyutlar
- Web: En az 120px genişlik
- Baskı: En az 2 inç (5cm) genişlik

### Kullanım Alanları
✅ Web sitesi navigasyonu (uygulandı)
✅ E-posta imzası
✅ Sosyal medya profilleri
✅ Kartvizitler
✅ Antetli kağıtlar
✅ Sunumlar

### Arka Plan Önerileri
- Beyaz veya açık renkli arka planlar idealdir
- Koyu arka planlarda renkleri tersine çevirmeniz gerekebilir

## Teknik Detaylar

- **Format**: SVG (Scalable Vector Graphics)
- **Boyut**: Responsive, her ekran için uygun
- **Renk Modu**: RGB
- **ViewBox**: 300x120
- **Bağımlılıklar**: Yok (React dışında)

## Destek

Logo ile ilgili sorularınız için:
- Dosya konumu: `src/assets/logos/KoptayLogo6-Executive.jsx`
- Kullanım örneği: `src/components/Nav.jsx`
- Tüm logolar: `/logo-showcase` sayfası

---

**Not**: Logo otomatik olarak navigasyon barına eklenmiştir ve hemen kullanıma hazırdır! 🎉
