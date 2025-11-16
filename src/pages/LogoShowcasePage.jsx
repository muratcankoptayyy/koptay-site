import KoptayLogoClassic from '../assets/logos/KoptayLogo1-Classic'
import KoptayLogoModern from '../assets/logos/KoptayLogo2-Modern'
import KoptayLogoPillars from '../assets/logos/KoptayLogo3-Pillars'
import KoptayLogoElegant from '../assets/logos/KoptayLogo4-Elegant'
import KoptayLogoPremiumBadge from '../assets/logos/KoptayLogo5-PremiumBadge'
import KoptayLogoExecutive from '../assets/logos/KoptayLogo6-Executive'
import KoptayLogoContemporary from '../assets/logos/KoptayLogo7-Contemporary'
import KoptayLogoPrestige from '../assets/logos/KoptayLogo8-Prestige'
import SEO from '../components/SEO'

const LogoShowcasePage = () => {
  const logos = [
    {
      id: 1,
      name: 'Klasik Tasarım',
      component: KoptayLogoClassic,
      description: 'Geleneksel hukuk firması logosu. Adalet terazisi ve kalkan sembolleri ile profesyonel ve güvenilir bir görünüm.',
      features: ['Adalet terazisi', 'Kalkan simgesi', 'Klasik tipografi', 'Kurumsal görünüm'],
      bestFor: 'Geleneksel ve kurumsal bir imaj arayan firmalar için ideal',
      isPremium: false
    },
    {
      id: 2,
      name: 'Modern Minimalist',
      component: KoptayLogoModern,
      description: 'Geometrik "K" harfi ile modern ve çağdaş bir tasarım. Minimalist yaklaşımla dikkat çekici.',
      features: ['Geometrik K harfi', 'Minimal tasarım', 'Modern çizgiler', 'Akılda kalıcı'],
      bestFor: 'Modern, dinamik ve yenilikçi bir imaj için uygun',
      isPremium: false
    },
    {
      id: 3,
      name: 'Klasik Sütunlar',
      component: KoptayLogoPillars,
      description: 'Üç Yunan sütunu ile güç, istikrar ve adaleti simgeleyen tasarım. Hukuk ve demokrasinin temel değerlerine gönderme.',
      features: ['Klasik sütunlar', 'Güç simgesi', 'İstikrar vurgusu', 'Tarihsel referans'],
      bestFor: 'Güçlü, köklü ve istikrarlı bir kurum imajı için',
      isPremium: false
    },
    {
      id: 4,
      name: 'Zarif Monogram',
      component: KoptayLogoElegant,
      description: 'İç içe geçmiş K harfi ve terazi tasarımı ile şık ve sofistike bir görünüm. Hatırlanabilir monogram.',
      features: ['Monogram tasarım', 'Terazi entegrasyonu', 'Altıgen çerçeve', 'Şık ve sofistike'],
      bestFor: 'Prestijli, lüks ve sofistike bir imaj için',
      isPremium: false
    },
    {
      id: 5,
      name: 'Premium Rozet',
      component: KoptayLogoPremiumBadge,
      description: 'Ultra-profesyonel dairesel rozet tasarımı. Zarafet ve prestiji bir arada sunan, yüksek kalite vurgusu yapan tasarım.',
      features: ['Dairesel rozet', 'Yasal kitap ikonu', 'Kavisli tipografi', 'Premium detaylar'],
      bestFor: 'Prestijli, seçkin ve yüksek kalite odaklı kurumlar için',
      isPremium: true
    },
    {
      id: 6,
      name: 'Executive Serif',
      component: KoptayLogoExecutive,
      description: 'Yüksek seviye yönetici tarzı, tipografi odaklı tasarım. Profesyonellik ve otoritenin en üst düzeyde vurgulandığı logo.',
      features: ['Premium tipografi', 'Minimalist adalet terazisi', 'Dekoratif köşe detayları', 'Yatay yerleşim'],
      bestFor: 'Üst düzey, kurumsal ve lider hukuk firmaları için',
      isPremium: true
    },
    {
      id: 7,
      name: 'Contemporary Law',
      component: KoptayLogoContemporary,
      description: 'Çağdaş ve temiz geometrik tasarım. Modern hukuk pratiğinin dinamizmini yansıtan, keskin çizgilerle tasarlanmış logo.',
      features: ['Geometrik çerçeve', 'Modern K tasarımı', 'Paragraf simgesi', 'Keskin profesyonellik'],
      bestFor: 'Modern, yenilikçi ve genç müvekkil kitlesi olan firmalar için',
      isPremium: true
    },
    {
      id: 8,
      name: 'Prestige Crest',
      component: KoptayLogoPrestige,
      description: 'Lüks arma tasarımı ile aristokrat görünüm. Defne dalları ve kalkan ile yüksek prestij ve güvenilirlik simgesi.',
      features: ['Heraldik kalkan', 'Defne dalları', 'Şerit banner', 'Arma tarzı'],
      bestFor: 'En prestijli, köklü ve lüks segment için',
      isPremium: true
    }
  ]

  return (
    <>
      <SEO 
        title="Logo Tasarımları - Koptay Hukuk Bürosu"
        description="Koptay Hukuk Bürosu için profesyonel logo tasarım seçenekleri"
        url="/logo-showcase"
      />

      {/* Header */}
      <section className="bg-gradient-to-br from-lawPrimary to-lawSecondary text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-5xl font-light mb-4 font-serif">
            Logo Tasarım Seçenekleri
          </h1>
          <p className="text-xl max-w-3xl mx-auto mb-4">
            Koptay Hukuk Bürosu için hazırlanmış profesyonel logo tasarımları
          </p>
          <p className="text-lg max-w-2xl mx-auto opacity-90">
            4 yeni premium tasarım eklendi! Daha sofistike ve prestijli seçenekler için aşağıya bakın.
          </p>
        </div>
      </section>

      {/* Logos Grid */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12">
            {logos.map((logo) => {
              const LogoComponent = logo.component
              return (
                <div 
                  key={logo.id}
                  className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-2xl transition-all duration-300"
                >
                  {/* Logo Display */}
                  <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-12 flex items-center justify-center">
                    <LogoComponent className="w-64 h-64" />
                  </div>
                  
                  {/* Logo Info */}
                  <div className="p-8">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-2xl font-semibold text-lawPrimary font-serif">
                        Seçenek {logo.id}: {logo.name}
                      </h3>
                      <div className="flex gap-2">
                        <span className="bg-lawSecondary text-white px-4 py-1 rounded-full text-sm">
                          SVG
                        </span>
                        {logo.isPremium && (
                          <span className="bg-gradient-to-r from-yellow-500 to-yellow-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                            ⭐ Premium
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <p className="text-gray-700 mb-6 leading-relaxed">
                      {logo.description}
                    </p>
                    
                    {/* Features */}
                    <div className="mb-6">
                      <h4 className="font-semibold text-lawPrimary mb-3">Özellikler:</h4>
                      <ul className="space-y-2">
                        {logo.features.map((feature, idx) => (
                          <li key={idx} className="flex items-center text-gray-600">
                            <svg className="w-5 h-5 text-lawSecondary mr-2" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    {/* Best For */}
                    <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r">
                      <p className="text-sm text-blue-900">
                        <strong>En Uygun:</strong> {logo.bestFor}
                      </p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Design Recommendations */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4 max-w-5xl">
          <h2 className="text-3xl font-serif text-lawPrimary mb-8 text-center">
            Logo Tasarım Önerileri ve Açıklamalar
          </h2>
          
          <div className="space-y-8">
            {/* Color Psychology */}
            <div className="bg-gray-50 p-6 rounded-lg">
              <h3 className="text-xl font-semibold text-lawPrimary mb-4 flex items-center">
                <svg className="w-6 h-6 mr-2 text-lawSecondary" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 2a2 2 0 00-2 2v11a3 3 0 106 0V4a2 2 0 00-2-2H4zm1 14a1 1 0 100-2 1 1 0 000 2zm5-1.757l4.9-4.9a2 2 0 000-2.828L13.485 5.1a2 2 0 00-2.828 0L10 5.757v8.486zM16 18H9.071l6-6H16a2 2 0 012 2v2a2 2 0 01-2 2z" clipRule="evenodd" />
                </svg>
                Renk Psikolojisi
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-lawPrimary mb-2">Koyu Gri-Mavi (#2D3748)</h4>
                  <p className="text-gray-700 text-sm">
                    Profesyonellik, güvenilirlik ve otoriteyi simgeler. Hukuk firmaları için ideal ana renk.
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-lawSecondary mb-2">Turkuaz (#548c8d)</h4>
                  <p className="text-gray-700 text-sm">
                    Güven, iletişim ve denge. Modern ve yaklaşılabilir bir imaj yaratır.
                  </p>
                </div>
              </div>
            </div>

            {/* Symbol Meanings */}
            <div className="bg-gray-50 p-6 rounded-lg">
              <h3 className="text-xl font-semibold text-lawPrimary mb-4 flex items-center">
                <svg className="w-6 h-6 mr-2 text-lawSecondary" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                Sembol Anlamları
              </h3>
              <ul className="space-y-3 text-gray-700">
                <li className="flex items-start">
                  <span className="text-lawSecondary mr-2">⚖️</span>
                  <span><strong>Adalet Terazisi:</strong> Hukukun temel simgesi, adalet ve denge</span>
                </li>
                <li className="flex items-start">
                  <span className="text-lawSecondary mr-2">🛡️</span>
                  <span><strong>Kalkan:</strong> Koruma, güvenlik ve müvekkil savunması</span>
                </li>
                <li className="flex items-start">
                  <span className="text-lawSecondary mr-2">🏛️</span>
                  <span><strong>Sütunlar:</strong> Güç, istikrar, demokrasi ve hukuk tarihi</span>
                </li>
                <li className="flex items-start">
                  <span className="text-lawSecondary mr-2">⬡</span>
                  <span><strong>Geometrik Şekiller:</strong> Düzen, kesinlik ve profesyonellik</span>
                </li>
              </ul>
            </div>

            {/* Usage Recommendations */}
            <div className="bg-blue-50 p-6 rounded-lg border-l-4 border-blue-500">
              <h3 className="text-xl font-semibold text-blue-900 mb-4">Kullanım Önerileri</h3>
              <div className="grid md:grid-cols-2 gap-4 text-sm text-blue-800">
                <div>
                  <h4 className="font-semibold mb-2">✅ Logo için uygun yerler:</h4>
                  <ul className="list-disc list-inside space-y-1">
                    <li>Web sitesi başlığı</li>
                    <li>Kartvizitler</li>
                    <li>Antetli kağıtlar</li>
                    <li>E-posta imzası</li>
                    <li>Sosyal medya profilleri</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">💡 İpuçları:</h4>
                  <ul className="list-disc list-inside space-y-1">
                    <li>SVG formatı her boyutta net görüntü</li>
                    <li>Kolay renk değişimi mümkün</li>
                    <li>Web performansı için optimize</li>
                    <li>Responsive tasarıma uyumlu</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Next Steps */}
      <section className="py-12 bg-gradient-to-br from-lawPrimary to-lawSecondary text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-serif mb-4">Sonraki Adımlar</h2>
          <p className="text-xl mb-6 max-w-2xl mx-auto">
            Beğendiğiniz logo tasarımını seçin, gerekirse özelleştirelim ve sitenize entegre edelim.
          </p>
          <div className="flex flex-col md:flex-row gap-4 justify-center">
            <button className="bg-white text-lawPrimary px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-all">
              Logo Seçimi Yap
            </button>
            <button className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-lawPrimary transition-all">
              Özelleştirme Talep Et
            </button>
          </div>
        </div>
      </section>
    </>
  )
}

export default LogoShowcasePage
