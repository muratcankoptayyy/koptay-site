"""
Uygulama sabitleri - İller, İlçeler, Adliyeler
"""

# Türkiye'nin 81 İli (Alfabetik)
CITIES = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", 
    "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", 
    "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", 
    "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", 
    "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", 
    "Gümüşhane", "Hakkâri", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir", 
    "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", 
    "Kilis", "Kırıkkale", "Kırklareli", "Kırşehir", "Kocaeli", "Konya", "Kütahya", 
    "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", 
    "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", 
    "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", 
    "Van", "Yalova", "Yozgat", "Zonguldak"
]

# İllere göre adliyeler (81 il)
COURTHOUSES = {
    "Ankara": [
        "Ankara Adliyesi",
        "Akyurt Adliyesi",
        "Bala Adliyesi",
        "Beypazarı Adliyesi",
        "Çubuk Adliyesi",
        "Elmadağ Adliyesi",
        "Gölbaşı Adliyesi",
        "Haymana Adliyesi",
        "Kalecik Adliyesi",
        "Kahramankazan Adliyesi",
        "Kızılcahamam Adliyesi",
        "Nallıhan Adliyesi",
        "Polatlı Adliyesi",
        "Ankara Batı Adliyesi",
        "Şereflikoçhisar Adliyesi"
    ],
    "İstanbul": [
        "Adalar Adliyesi",
        "Bakırköy Adliyesi",
        "Beykoz Adliyesi",
        "Büyükçekmece Adliyesi",
        "Çatalca Adliyesi",
        "Eyüp Adliyesi",
        "Gaziosmanpaşa Adliyesi",
        "İstanbul Anadolu Adliyesi",
        "Küçükçekmece Adliyesi",
        "Silivri Adliyesi",
        "Şile Adliyesi",
        "İstanbul Adliyesi"
    ],
    "İzmir": [
        "İzmir Adliyesi",
        "Aliağa Adliyesi",
        "Bayındır Adliyesi",
        "Bergama Adliyesi",
        "Çeşme Adliyesi",
        "Dikili Adliyesi",
        "Foça Adliyesi",
        "Karaburun Adliyesi",
        "Karşıyaka Adliyesi",
        "Kemalpaşa Adliyesi",
        "Kınık Adliyesi",
        "Kiraz Adliyesi",
        "Menderes Adliyesi",
        "Menemen Adliyesi",
        "Ödemiş Adliyesi",
        "Seferihisar Adliyesi",
        "Selçuk Adliyesi",
        "Tire Adliyesi",
        "Torbalı Adliyesi",
        "Urla Adliyesi"
    ],
    "Adana": [
        "Adana Adliyesi",
        "Aladağ Adliyesi",
        "Ceyhan Adliyesi",
        "Feke Adliyesi",
        "İmamoğlu Adliyesi",
        "Karaisalı Adliyesi",
        "Karataş Adliyesi",
        "Kozan Adliyesi",
        "Pozantı Adliyesi",
        "Tufanbeyli Adliyesi",
        "Yumurtalık Adliyesi"
    ],
    "Adıyaman": [
        "Adıyaman Adliyesi",
        "Besni Adliyesi",
        "Gerger Adliyesi",
        "Gölbaşı(Adıyaman) Adliyesi",
        "Kahta Adliyesi"
    ],
    "Afyonkarahisar": [
        "Afyonkarahisar Adliyesi",
        "Bolvadin Adliyesi",
        "Çay Adliyesi",
        "Dazkırı Adliyesi",
        "Dinar Adliyesi",
        "Emirdağ Adliyesi",
        "İscehisar Adliyesi",
        "Sandıklı Adliyesi",
        "Sinanpaşa Adliyesi",
        "Şuhut Adliyesi"
    ],
    "Ağrı": [
        "Ağrı Adliyesi",
        "Diyadin Adliyesi",
        "Doğubayazıt Adliyesi",
        "Eleşkirt Adliyesi",
        "Patnos Adliyesi",
        "Taşlıçay Adliyesi",
        "Tutak Adliyesi"
    ],
    "Aksaray": [
        "Aksaray Adliyesi",
        "Eskil Adliyesi",
        "Ortaköy (Aksaray) Adliyesi"
    ],
    "Amasya": [
        "Amasya Adliyesi",
        "Gümüşhacıköy Adliyesi",
        "Merzifon Adliyesi",
        "Suluova Adliyesi",
        "Taşova Adliyesi"
    ],
    "Antalya": [
        "Antalya Adliyesi",
        "Akseki Adliyesi",
        "Alanya Adliyesi",
        "Elmalı Adliyesi",
        "Finike Adliyesi",
        "Gazipaşa Adliyesi",
        "Gündoğmuş Adliyesi",
        "Demre Adliyesi",
        "Kaş Adliyesi",
        "Kemer Adliyesi",
        "Korkuteli Adliyesi",
        "Kumluca Adliyesi",
        "Manavgat Adliyesi",
        "Serik Adliyesi"
    ],
    "Ardahan": [
        "Ardahan Adliyesi",
        "Göle Adliyesi",
        "Hanak Adliyesi",
        "Posof Adliyesi"
    ],
    "Artvin": [
        "Artvin Adliyesi",
        "Arhavi Adliyesi",
        "Borçka Adliyesi",
        "Hopa Adliyesi",
        "Şavşat Adliyesi",
        "Yusufeli Adliyesi"
    ],
    "Aydın": [
        "Aydın Adliyesi",
        "Bozdoğan Adliyesi",
        "Çine Adliyesi",
        "Didim(Yenihisar) Adliyesi",
        "Germencik Adliyesi",
        "Karacasu Adliyesi",
        "Kuşadası Adliyesi",
        "Nazilli Adliyesi",
        "Söke Adliyesi"
    ],
    "Balıkesir": [
        "Balıkesir Adliyesi",
        "Ayvalık Adliyesi",
        "Bandırma Adliyesi",
        "Bigadiç Adliyesi",
        "Burhaniye Adliyesi",
        "Dursunbey Adliyesi",
        "Edremit Adliyesi",
        "Erdek Adliyesi",
        "Gönen(Balıkesir) Adliyesi",
        "İvrindi Adliyesi",
        "Kepsut Adliyesi",
        "Manyas Adliyesi",
        "Marmara Adliyesi",
        "Savaştepe Adliyesi",
        "Sındırgı Adliyesi",
        "Susurluk Adliyesi"
    ],
    "Batman": [
        "Batman Adliyesi",
        "Gercüş Adliyesi",
        "Kozluk Adliyesi",
        "Sason Adliyesi"
    ],
    "Bartın": [
        "Bartın Adliyesi",
        "Amasra Adliyesi",
        "Kurucaşile Adliyesi",
        "Ulus Adliyesi"
    ],
    "Bayburt": [
        "Bayburt Adliyesi"
    ],
    "Bilecik": [
        "Bilecik Adliyesi",
        "Bozüyük Adliyesi",
        "Gölpazarı Adliyesi",
        "Osmaneli Adliyesi",
        "Söğüt Adliyesi"
    ],
    "Bingöl": [
        "Bingöl Adliyesi",
        "Genç Adliyesi",
        "Karlıova Adliyesi",
        "Kiğı Adliyesi",
        "Solhan Adliyesi"
    ],
    "Bitlis": [
        "Bitlis Adliyesi",
        "Adilcevaz Adliyesi",
        "Ahlat Adliyesi",
        "Güroymak Adliyesi",
        "Hizan Adliyesi",
        "Mutki Adliyesi",
        "Tatvan Adliyesi"
    ],
    "Bolu": [
        "Bolu Adliyesi",
        "Gerede Adliyesi",
        "Göynük Adliyesi",
        "Mengen Adliyesi",
        "Mudurnu Adliyesi"
    ],
    "Burdur": [
        "Burdur Adliyesi",
        "Bucak Adliyesi",
        "Gölhisar Adliyesi",
        "Tefenni Adliyesi",
        "Yeşilova Adliyesi"
    ],
    "Bursa": [
        "Bursa Adliyesi",
        "Gemlik Adliyesi",
        "İnegöl Adliyesi",
        "İznik Adliyesi",
        "Karacabey Adliyesi",
        "Keles Adliyesi",
        "Mudanya Adliyesi",
        "Mustafakemalpaşa Adliyesi",
        "Orhaneli Adliyesi",
        "Orhangazi Adliyesi",
        "Yenişehir Adliyesi"
    ],
    "Çanakkale": [
        "Çanakkale Adliyesi",
        "Ayvacık Adliyesi",
        "Bayramiç Adliyesi",
        "Biga Adliyesi",
        "Çan Adliyesi",
        "Ezine Adliyesi",
        "Gelibolu Adliyesi",
        "Gökçeada Adliyesi",
        "Lapseki Adliyesi",
        "Yenice(Çanakkale) Adliyesi"
    ],
    "Çankırı": [
        "Çankırı Adliyesi",
        "Çerkeş Adliyesi",
        "Ilgaz Adliyesi",
        "Kurşunlu Adliyesi",
        "Şabanözü Adliyesi"
    ],
    "Çorum": [
        "Çorum Adliyesi",
        "Alaca Adliyesi",
        "Bayat(Çorum) Adliyesi",
        "İskilip Adliyesi",
        "Kargı Adliyesi",
        "Osmancık Adliyesi",
        "Sungurlu Adliyesi"
    ],
    "Denizli": [
        "Denizli Adliyesi",
        "Acıpayam Adliyesi",
        "Buldan Adliyesi",
        "Çal Adliyesi",
        "Çameli Adliyesi",
        "Çardak Adliyesi",
        "Çivril Adliyesi",
        "Kale(Denizli) Adliyesi",
        "Sarayköy Adliyesi",
        "Tavas Adliyesi"
    ],
    "Diyarbakır": [
        "Diyarbakır Adliyesi",
        "Bismil Adliyesi",
        "Çermik Adliyesi",
        "Çınar Adliyesi",
        "Çüngüş Adliyesi",
        "Dicle Adliyesi",
        "Eğil Adliyesi",
        "Ergani Adliyesi",
        "Hani Adliyesi",
        "Hazro Adliyesi",
        "Kulp Adliyesi",
        "Lice Adliyesi",
        "Silvan Adliyesi"
    ],
    "Düzce": [
        "Düzce Adliyesi",
        "Akçakoca Adliyesi",
        "Yığılca Adliyesi"
    ],
    "Edirne": [
        "Edirne Adliyesi",
        "Enez Adliyesi",
        "İpsala Adliyesi",
        "Keşan Adliyesi",
        "Uzunköprü Adliyesi"
    ],
    "Elazığ": [
        "Elazığ Adliyesi",
        "Karakoçan Adliyesi",
        "Keban Adliyesi",
        "Kovancılar Adliyesi",
        "Maden Adliyesi",
        "Palu Adliyesi"
    ],
    "Erzincan": [
        "Erzincan Adliyesi",
        "Çayırlı Adliyesi",
        "İliç Adliyesi",
        "Kemah Adliyesi",
        "Kemaliye Adliyesi",
        "Refahiye Adliyesi",
        "Tercan Adliyesi"
    ],
    "Erzurum": [
        "Erzurum Adliyesi",
        "Aşkale Adliyesi",
        "Çat Adliyesi",
        "Hınıs Adliyesi",
        "Horasan Adliyesi",
        "İspir Adliyesi",
        "Karayazı Adliyesi",
        "Oltu Adliyesi",
        "Pasinler Adliyesi",
        "Şenkaya Adliyesi",
        "Tekman Adliyesi",
        "Tortum Adliyesi"
    ],
    "Eskişehir": [
        "Eskişehir Adliyesi",
        "Beylikova Adliyesi",
        "Çifteler Adliyesi",
        "Mihalıççık Adliyesi",
        "Sivrihisar Adliyesi"
    ],
    "Gaziantep": [
        "Gaziantep Adliyesi",
        "Araban Adliyesi",
        "İslahiye Adliyesi",
        "Nizip Adliyesi",
        "Nurdağı Adliyesi"
    ],
    "Giresun": [
        "Giresun Adliyesi",
        "Alucra Adliyesi",
        "Bulancak Adliyesi",
        "Dereli Adliyesi",
        "Espiye Adliyesi",
        "Görele Adliyesi",
        "Şebinkarahisar Adliyesi",
        "Tirebolu Adliyesi"
    ],
    "Gümüşhane": [
        "Gümüşhane Adliyesi",
        "Kelkit Adliyesi",
        "Şiran Adliyesi",
        "Torul Adliyesi"
    ],
    "Hakkâri": [
        "Hakkari Adliyesi",
        "Çukurca Adliyesi",
        "Şemdinli Adliyesi",
        "Yüksekova Adliyesi"
    ],
    "Hatay": [
        "Hatay Adliyesi",
        "Altınözü Adliyesi",
        "Dörtyol Adliyesi",
        "Erzin Adliyesi",
        "Hassa Adliyesi",
        "İskenderun Adliyesi",
        "Kırıkhan Adliyesi",
        "Reyhanlı Adliyesi",
        "Samandağ Adliyesi",
        "Yayladağı Adliyesi"
    ],
    "Iğdır": [
        "Iğdır Adliyesi",
        "Aralık Adliyesi",
        "Tuzluca Adliyesi"
    ],
    "Isparta": [
        "Isparta Adliyesi",
        "Eğirdir Adliyesi",
        "Keçiborlu Adliyesi",
        "Senirkent Adliyesi",
        "Sütçüler Adliyesi",
        "Şarkikaraağaç Adliyesi",
        "Yalvaç Adliyesi"
    ],
    "Mersin": [
        "Mersin Adliyesi",
        "Anamur Adliyesi",
        "Aydıncık(Mersin) Adliyesi",
        "Erdemli Adliyesi",
        "Gülnar Adliyesi",
        "Mut Adliyesi",
        "Silifke Adliyesi",
        "Tarsus Adliyesi"
    ],
    "Kars": [
        "Kars Adliyesi",
        "Arpaçay Adliyesi",
        "Digor Adliyesi",
        "Kağızman Adliyesi",
        "Sarıkamış Adliyesi",
        "Selim Adliyesi"
    ],
    "Karaman": [
        "Karaman Adliyesi",
        "Ermenek Adliyesi",
        "Sarıveliler Adliyesi"
    ],
    "Kastamonu": [
        "Kastamonu Adliyesi",
        "Araç Adliyesi",
        "Azdavay Adliyesi",
        "Cide Adliyesi",
        "Devrekani Adliyesi",
        "İnebolu Adliyesi",
        "Küre Adliyesi",
        "Taşköprü Adliyesi",
        "Tosya Adliyesi"
    ],
    "Kayseri": [
        "Kayseri Adliyesi",
        "Bünyan Adliyesi",
        "Develi Adliyesi",
        "İncesu Adliyesi",
        "Pınarbaşı(Kayseri) Adliyesi",
        "Sarıoğlan Adliyesi",
        "Sarız Adliyesi",
        "Tomarza Adliyesi",
        "Yahyalı Adliyesi",
        "Yeşilhisar Adliyesi"
    ],
    "Kırklareli": [
        "Kırklareli Adliyesi",
        "Babaeski Adliyesi",
        "Demirköy Adliyesi",
        "Lüleburgaz Adliyesi",
        "Pınarhisar Adliyesi",
        "Vize Adliyesi"
    ],
    "Kilis": [
        "Kilis Adliyesi"
    ],
    "Kırıkkale": [
        "Kırıkkale Adliyesi",
        "Delice Adliyesi",
        "Keskin Adliyesi",
        "Sulakyurt Adliyesi"
    ],
    "Kırşehir": [
        "Kırşehir Adliyesi",
        "Kaman Adliyesi",
        "Mucur Adliyesi"
    ],
    "Kocaeli": [
        "Kocaeli Adliyesi",
        "Gebze Adliyesi",
        "Gölcük Adliyesi",
        "Kandıra Adliyesi",
        "Karamürsel Adliyesi",
        "Körfez Adliyesi"
    ],
    "Konya": [
        "Konya Adliyesi",
        "Akşehir Adliyesi",
        "Beyşehir Adliyesi",
        "Bozkır Adliyesi",
        "Cihanbeyli Adliyesi",
        "Çumra Adliyesi",
        "Doğanhisar Adliyesi",
        "Ereğli(Konya) Adliyesi",
        "Hadim Adliyesi",
        "Ilgın Adliyesi",
        "Kadınhanı Adliyesi",
        "Karapınar Adliyesi",
        "Kulu Adliyesi",
        "Sarayönü Adliyesi",
        "Seydişehir Adliyesi",
        "Yunak Adliyesi"
    ],
    "Kütahya": [
        "Kütahya Adliyesi",
        "Altıntaş Adliyesi",
        "Emet Adliyesi",
        "Gediz Adliyesi",
        "Simav Adliyesi",
        "Tavşanlı Adliyesi"
    ],
    "Malatya": [
        "Malatya Adliyesi",
        "Akçadağ Adliyesi",
        "Arapgir Adliyesi",
        "Darende Adliyesi",
        "Doğanşehir Adliyesi",
        "Hekimhan Adliyesi",
        "Pütürge Adliyesi"
    ],
    "Manisa": [
        "Manisa Adliyesi",
        "Akhisar Adliyesi",
        "Alaşehir Adliyesi",
        "Demirci Adliyesi",
        "Gördes Adliyesi",
        "Kırkağaç Adliyesi",
        "Kula Adliyesi",
        "Salihli Adliyesi",
        "Sarıgöl Adliyesi",
        "Saruhanlı Adliyesi",
        "Selendi Adliyesi",
        "Soma Adliyesi",
        "Turgutlu Adliyesi"
    ],
    "Kahramanmaraş": [
        "Kahramanmaraş Adliyesi",
        "Afşin Adliyesi",
        "Andırın Adliyesi",
        "Elbistan Adliyesi",
        "Göksun Adliyesi",
        "Pazarcık Adliyesi",
        "Türkoğlu Adliyesi"
    ],
    "Karabük": [
        "Karabük Adliyesi",
        "Eskipazar Adliyesi",
        "Safranbolu Adliyesi",
        "Yenice (Karabük) Adliyesi"
    ],
    "Mardin": [
        "Mardin Adliyesi",
        "Dargeçit Adliyesi",
        "Derik Adliyesi",
        "Kızıltepe Adliyesi",
        "Mazıdağı Adliyesi",
        "Midyat Adliyesi",
        "Nusaybin Adliyesi",
        "Ömerli Adliyesi",
        "Savur Adliyesi"
    ],
    "Muğla": [
        "Muğla Adliyesi",
        "Bodrum Adliyesi",
        "Datça Adliyesi",
        "Fethiye Adliyesi",
        "Köyceğiz Adliyesi",
        "Marmaris Adliyesi",
        "Milas Adliyesi",
        "Ortaca Adliyesi",
        "Yatağan Adliyesi",
        "Seydikemer Adliyesi"
    ],
    "Muş": [
        "Muş Adliyesi",
        "Bulanık Adliyesi",
        "Malazgirt Adliyesi",
        "Varto Adliyesi"
    ],
    "Nevşehir": [
        "Nevşehir Adliyesi",
        "Avanos Adliyesi",
        "Derinkuyu Adliyesi",
        "Gülşehir Adliyesi",
        "Hacıbektaş Adliyesi",
        "Kozaklı Adliyesi",
        "Ürgüp Adliyesi"
    ],
    "Niğde": [
        "Niğde Adliyesi",
        "Bor Adliyesi",
        "Çamardı Adliyesi",
        "Çiftlik Adliyesi",
        "Ulukışla Adliyesi"
    ],
    "Ordu": [
        "Ordu Adliyesi",
        "Akkuş Adliyesi",
        "Aybastı Adliyesi",
        "Fatsa Adliyesi",
        "Gölköy Adliyesi",
        "Gürgentepe Adliyesi",
        "Korgan Adliyesi",
        "Kumru Adliyesi",
        "Mesudiye Adliyesi",
        "Perşembe Adliyesi",
        "Ünye Adliyesi"
    ],
    "Osmaniye": [
        "Osmaniye Adliyesi",
        "Bahçe Adliyesi",
        "Düziçi Adliyesi",
        "Kadirli Adliyesi"
    ],
    "Rize": [
        "Rize Adliyesi",
        "Çayeli Adliyesi",
        "Kalkandere Adliyesi",
        "Pazar (Rize) Adliyesi"
    ],
    "Sakarya": [
        "Sakarya Adliyesi",
        "Akyazı Adliyesi",
        "Ferizli Adliyesi",
        "Geyve Adliyesi",
        "Hendek Adliyesi",
        "Karasu Adliyesi",
        "Kaynarca Adliyesi",
        "Kocaali (Sakarya) Adliyesi",
        "Pamukova Adliyesi",
        "Sapanca Adliyesi"
    ],
    "Samsun": [
        "Samsun Adliyesi",
        "Alaçam Adliyesi",
        "Bafra Adliyesi",
        "Çarşamba Adliyesi",
        "Havza Adliyesi",
        "Kavak Adliyesi",
        "Ladik Adliyesi",
        "Terme Adliyesi",
        "Vezirköprü Adliyesi"
    ],
    "Siirt": [
        "Siirt Adliyesi",
        "Baykan Adliyesi",
        "Eruh Adliyesi",
        "Kurtalan Adliyesi",
        "Pervari Adliyesi",
        "Şirvan Adliyesi"
    ],
    "Sinop": [
        "Sinop Adliyesi",
        "Ayancık Adliyesi",
        "Boyabat Adliyesi",
        "Durağan Adliyesi",
        "Gerze (Sinop) Adliyesi",
        "Türkeli Adliyesi"
    ],
    "Sivas": [
        "Sivas Adliyesi",
        "Divriği Adliyesi",
        "Gemerek Adliyesi",
        "Gürün Adliyesi",
        "İmranlı Adliyesi",
        "Kangal Adliyesi",
        "Koyulhisar Adliyesi",
        "Suşehri Adliyesi",
        "Şarkışla Adliyesi",
        "Yıldızeli Adliyesi",
        "Zara Adliyesi"
    ],
    "Tekirdağ": [
        "Tekirdağ Adliyesi",
        "Çerkezköy Adliyesi",
        "Çorlu Adliyesi",
        "Hayrabolu Adliyesi",
        "Malkara Adliyesi",
        "Marmaraereğlisi Adliyesi",
        "Muratlı Adliyesi",
        "Saray (Tekirdağ) Adliyesi",
        "Şarköy Adliyesi"
    ],
    "Tokat": [
        "Tokat Adliyesi",
        "Almus Adliyesi",
        "Artova Adliyesi",
        "Erbaa Adliyesi",
        "Niksar Adliyesi",
        "Reşadiye Adliyesi",
        "Turhal Adliyesi",
        "Zile Adliyesi"
    ],
    "Trabzon": [
        "Trabzon Adliyesi",
        "Akçaabat Adliyesi",
        "Araklı Adliyesi",
        "Çaykara Adliyesi",
        "Maçka Adliyesi",
        "Of Adliyesi",
        "Sürmene Adliyesi",
        "Tonya Adliyesi",
        "Vakfıkebir Adliyesi"
    ],
    "Tunceli": [
        "Tunceli Adliyesi",
        "Çemişgezek Adliyesi",
        "Hozat Adliyesi",
        "Mazgirt Adliyesi",
        "Nazımiye Adliyesi",
        "Ovacık (Tunceli) Adliyesi",
        "Pertek Adliyesi",
        "Pülümür Adliyesi"
    ],
    "Şanlıurfa": [
        "Şanlıurfa Adliyesi",
        "Akçakale Adliyesi",
        "Birecik Adliyesi",
        "Bozova Adliyesi",
        "Ceylanpınar Adliyesi",
        "Halfeti Adliyesi",
        "Harran Adliyesi",
        "Hilvan Adliyesi",
        "Siverek Adliyesi",
        "Suruç Adliyesi",
        "Viranşehir Adliyesi"
    ],
    "Şırnak": [
        "Şırnak Adliyesi",
        "Beytüşşebap Adliyesi",
        "Cizre Adliyesi",
        "İdil Adliyesi",
        "Silopi Adliyesi",
        "Uludere Adliyesi"
    ],
    "Uşak": [
        "Uşak Adliyesi",
        "Banaz Adliyesi",
        "Eşme Adliyesi",
        "Sivaslı Adliyesi"
    ],
    "Van": [
        "Van Adliyesi",
        "Bahçesaray Adliyesi",
        "Başkale Adliyesi",
        "Çaldıran Adliyesi",
        "Çatak Adliyesi",
        "Erciş Adliyesi",
        "Gevaş Adliyesi",
        "Gürpınar Adliyesi",
        "Muradiye Adliyesi",
        "Özalp Adliyesi",
        "Saray (Van) Adliyesi"
    ],
    "Yalova": [
        "Yalova Adliyesi"
    ],
    "Yozgat": [
        "Yozgat Adliyesi",
        "Akdağmadeni Adliyesi",
        "Boğazlıyan Adliyesi",
        "Çayıralan Adliyesi",
        "Çekerek Adliyesi",
        "Sarıkaya Adliyesi",
        "Sorgun Adliyesi",
        "Şefaatli Adliyesi",
        "Yerköy Adliyesi"
    ],
    "Zonguldak": [
        "Zonguldak Adliyesi",
        "Alaplı Adliyesi",
        "Çaycuma Adliyesi",
        "Devrek Adliyesi",
        "KDZ.Ereğli (Zonguldak) Adliyesi",
        "Gökçebey Adliyesi"
    ]
}

# Baro listesi (15 büyük baro)
BAR_ASSOCIATIONS = [
    "Adana Barosu",
    "Ankara Barosu",
    "Antalya Barosu",
    "Bursa Barosu",
    "Diyarbakır Barosu",
    "Eskişehir Barosu",
    "Gaziantep Barosu",
    "Hatay Barosu",
    "İstanbul Barosu",
    "İzmir Barosu",
    "Kayseri Barosu",
    "Kocaeli Barosu",
    "Konya Barosu",
    "Mersin Barosu",
    "Şanlıurfa Barosu"
]

# İlan kategorileri
POST_CATEGORIES = [
    "Ceza Hukuku",
    "Aile Hukuku",
    "Ticaret Hukuku",
    "İcra İflas Hukuku",
    "İdare Hukuku",
    "İş Hukuku",
    "Gayrimenkul Hukuku",
    "Sözleşmeler Hukuku",
    "Tüketici Hukuku",
    "Miras Hukuku",
    "Vergi Hukuku",
    "Sigorta Hukuku",
    "Fikri Mülkiyet Hukuku",
    "Bankacılık Hukuku",
    "Ceza Muhakemesi",
    "Hukuk Muhakemesi",
    "Diğer"
]

# Aciliyet seviyeleri
URGENCY_LEVELS = {
    'normal': 'Normal',
    'urgent': 'Acil',
    'very_urgent': 'Çok Acil'
}

# Görev kategorisi tanımlamaları
TASK_CATEGORY_DEFINITIONS = {
    'durusma': {
        'label': 'Duruşma',
        'description': 'Mahkeme duruşmasına katılım'
    },
    'tahsilat': {
        'label': 'Tahsilat',
        'description': 'Alacak tahsilatı işlemleri'
    },
    'keşif': {
        'label': 'Keşif',
        'description': 'Mahkeme keşif işlemleri'
    },
    'tebligat': {
        'label': 'Tebligat',
        'description': 'Tebligat işlemleri'
    },
    'icra_takibi': {
        'label': 'İcra Takibi',
        'description': 'İcra takip işlemleri'
    },
    'diger': {
        'label': 'Diğer',
        'description': 'Diğer hukuki işlemler'
    }
}

# Görev kategorisi seçenekleri
TASK_CATEGORY_OPTIONS = list(TASK_CATEGORY_DEFINITIONS.keys())

# Kategori kısaltmaları
CATEGORY_ABBREVIATIONS = {
    'durusma': 'DRŞ',
    'tahsilat': 'THS',
    'keşif': 'KŞF',
    'tebligat': 'TBL',
    'icra_takibi': 'İCR',
    'diger': 'DĞR'
}
