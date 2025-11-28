import Image from 'next/image';
import Link from 'next/link';
import {useTheme} from 'next-themes';
import {useSelector} from 'react-redux';
import {useEffect, useState} from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination, Autoplay } from 'swiper';
import request from '@/utils/request';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';

const heroContents = [
	{
		title: "CMK Benzeri Sıralama Sistemi",
		description: "CMK benzeri sıralama algoritması ile çalışan, hak kaybı yaşamadan avukatların birbirine tevkil görevi verip alabileceği tevkil platformu TevkilApp'e hoş geldiniz.",
		image: "https://cdn.tevkilapp.com/uploads/tevkilapp-home-banner-1.png"
	},
	{
		title: "Adil ve Şeffaf Tevkil Sistemi",
		description: "Türkiye'nin en adil ve şeffaf tevkil platformunda, sıra beklemeden, hak kaybı yaşamadan tevkil görevi alabilir ve verebilirsiniz.",
		image: "https://cdn.tevkilapp.com/uploads/tevkilapp-home-banner-2.png"
	},
	{
		title: "Hızlı ve Güvenilir Tevkil",
		description: "TevkilApp ile artık tevkil görevlerini hızlı ve güvenilir bir şekilde yönetebilir, avukatlık mesleğinizi daha verimli hale getirebilirsiniz.",
		image: "https://cdn.tevkilapp.com/uploads/tevkilapp-home-banner-3.png"
	},
	{
		title: "Hızlı ve Güvenilir Tevkil",
		description: "TevkilApp ile artık tevkil görevlerini hızlı ve güvenilir bir şekilde yönetebilir, avukatlık mesleğinizi daha verimli hale getirebilirsiniz.",
		image: "https://cdn.tevkilapp.com/uploads/tevkilapp-home-banner-4.png"
	}
];

const randomNameList = [
	"Ahmet Y.", "Melda Z.", "Berk A.", "Sena K.", "Emir T.",
  "İlayda M.", "Mert B.", "Ceren D.", "Deniz E.", "Zeynep S.",
  "Burak G.", "Dilara C.", "Kerem P.", "Ece L.", "Okan R.",
  "Selin U.", "Can V.", "Elif H.", "Alp O.", "Büşra Y.",
  "Tuna F.", "Aslı J.", "Oğuz I.", "Derya N.", "Eren Q.",
  "Sude X.", "Yiğit W.", "İrem Ş.", "Hakan Ç.", "Bora Ü.",
  "Esra Ö.", "Arda Ğ.", "Beyza İ.", "Tolga Ü.", "Damla Ç.",
  "Kaan Ş.", "Sevgi Ö.", "Batuhan Ğ.", "Hande İ.", "Onur Ü.",
  "Nisan Ç.", "Volkan Ş.", "Selma Ö.", "Serkan Ğ.", "Nazlı İ.",
  "Baran Ü.", "Gizem Ç.", "Yasin Ş.", "Buse Ö.", "Levent Ğ."
];

const randomActionList = [
	"Tevkil yayınladı.",
	"Kayıt oldu.",
	"Tevkil görevi aldı.",
	"Kayıt oldu.",
	"Kayıt oldu.",
];

const getInitials = (fullName) => {
	if (!fullName) return '';
	
	// İsmi boşluklara göre böl
	const parts = fullName.split(' ');
	
	// İsim ve soyisim parçalarını al
	const firstName = parts[0] || '';
	const lastName = parts[parts.length - 1] || '';
	
	// İlk harfleri al ve büyük harfe çevir
	const firstInitial = firstName.charAt(0).toUpperCase();
	const lastInitial = lastName.charAt(0).toUpperCase();
	
	// İki harfli kısaltmayı döndür
	return `${firstInitial}${lastInitial}`;
};

const Hero_7 = () => {
	const {theme, setTheme} = useTheme();
	const user = useSelector((state) => state.user.user);
	const [loading, setLoading] = useState(true);
	const [currentIndex, setCurrentIndex] = useState(0);
	const [currentContent, setCurrentContent] = useState(heroContents[0]);
	const [progress, setProgress] = useState(0);
	const [activities, setActivities] = useState([]);

	useEffect(() => {
		const fetchActivities = async () => {
			try {
				const response = await request('/activity', 'GET', null, false, false, true, 5);
				console.log(response);
				if (response) {

					

					const activities = response.map(activity => ({
						name: activity.name,
						content: activity.content,
						image: activity.image,
						two_letters: activity.two_letters
					}));

					setActivities(response);
				}
			} catch (error) {
				console.error('Aktivite verileri yüklenirken hata oluştu:', error);
			}
		};

		// fetchActivities();
	}, []);

	useEffect(() => {
		if (user) {
			setLoading(false);
		}
	}, [user]);

	useEffect(() => {
		const progressInterval = setInterval(() => {
			setProgress((prevProgress) => {
				if (prevProgress >= 100) {
					return 0;
				}
				return prevProgress + (100 / (6500 / 100)); // Her 100ms'de bir artış
			});
		}, 100);

		const contentInterval = setInterval(() => {
			setProgress(0);
			setCurrentIndex((prevIndex) => (prevIndex + 1) % heroContents.length);
			setCurrentContent(heroContents[currentIndex]);
		}, 6000);

		return () => {
			clearInterval(contentInterval);
			clearInterval(progressInterval);
		};
	}, [currentIndex]);

	return (
		<>
			{/* <!-- Hero --> */}
			<section className="relative pb-12 pt-20 lg:pt-48">
				<picture className="pointer-events-none absolute inset-x-0 top-0 -z-10 dark:hidden ">
					<Image
						width={1519}
						height={773}
						priority
						src="https://cdn.tevkilapp.com/images/gradient.jpg"
						alt="gradient"
						className="h-full w-full object-cover"
					/>
				</picture>
				<picture className="pointer-events-none absolute inset-x-0 top-0 -z-10 hidden dark:block">
					<Image
						width={1519}
						height={773}
						priority
						className="h-full w-full"
						src="https://cdn.tevkilapp.com/images/gradient_dark.jpg"
						alt="gradient dark"
					/>
				</picture>
				<Image
					width={613}
					height={415}
					src="https://cdn.tevkilapp.com/images/patterns/pattern_donut.png"
					alt="pattern donut"
					className="absolute right-0 top-0 -z-10"
				/>

				 <div className="ml-auto mr-auto h-full max-w-[91rem] px-4 mt-24 sm:mt-0">
					{/*
					<div className="mb-0 sm:mb-8 swiper-container -mt-20 h-[100px]">
						<div className='flex items-center justify-start gap-3 mb-0'>
							<h2 className='text-lg font-bold font-display text-jacarta-700 dark:text-white'>TevkilApp'de Neler Oluyor?</h2>
						</div>
						<Swiper
							modules={[Navigation, Pagination, Autoplay]}
							spaceBetween={10}
							slidesPerView={7}
							navigation={{
								nextEl: '.swiper-button-next .hidden',
								prevEl: '.swiper-button-prev .hidden',
							}}
							pagination={{ 
								clickable: true,
								el: '.swiper-pagination'
							}}
							autoplay={{
								delay: 3000,
								disableOnInteraction: false,
							}}
							loop={false}
							centeredSlides={false}
							breakpoints={{
								320: {
									slidesPerView: 2,
									spaceBetween: 10
								},
								640: {
									slidesPerView: 3,
									spaceBetween: 10
								},
								768: {
									slidesPerView: 4,
									spaceBetween: 10
								},
								1024: {
									slidesPerView: 5,
									spaceBetween: 10
								},
								1280: {
									slidesPerView: 6,
									spaceBetween: 10
								},
							}}
							className="mySwiper hero-swiper"
						>
							{activities.map((activity, index) => (
								<SwiperSlide key={index}>
									<div className="bg-white/40 hover:bg-white/80 cursor-pointer border border-white/50 dark:bg-jacarta-700 rounded-lg p-3 shadow-lg mb-5 w-full">
										<div className='flex items-center justify-start gap-3'>
											<Image 
												src={activity.image && activity.image.length > 5 ? activity.image : `https://api.tevkilapp.com/avatar/${getInitials(activity.name)}`} 
												alt="tevkilapp-banner" 
												width={100} 
												height={100} 
												className='rounded-full w-8 h-8 object-cover' 
											/>
											<div className='flex flex-col items-start justify-center'>
												<div className='text-sm font-semibold text-jacarta-700 dark:text-white'>Av. {activity.name}</div>
												<p className='text-xs text-jacarta-500 dark:text-jacarta-200'>{activity.content}</p>
											</div>
										</div>
									</div>
								</SwiperSlide>
							))}
						</Swiper>
						<div className="swiper-pagination"></div>
						<div className="swiper-button-next"></div>
						<div className="swiper-button-prev"></div>
					</div> */}

					<div className="grid h-full items-center gap-4 lg:grid-cols-12">
						<div
							className="sm:col-span-5 col-span-12 flex h-full flex-col items-center justify-center py-10 lg:items-start lg:py-20">
							<p className="mb-10 text-xs font-bold uppercase text-jacarta-500 dark:text-jacarta-200">
								TevkilApp.com&apos;u keşfedin
							</p>
							<h1 className="mb-6 text-center font-display text-5xl text-jacarta-700 dark:text-white lg:text-left lg:text-6xl transition-opacity duration-500 ease-in-out">
								{currentContent.title}
							</h1>
							<p className="mb-8 max-w-md text-center text-lg dark:text-jacarta-200 lg:text-left transition-opacity duration-500 ease-in-out">
								{currentContent.description}
							</p>
							<div
								className="flex sm:space-x-4 sm:flex-row flex-col items-center w-full sm:gap-0 sm:items-start sm:justify-normal gap-4 justify-center">
								{!user ? (
									<>
										<Link
											href="/gorev-olustur"
											className="flex items-center gap-2 rounded-full bg-blue-600 py-3 px-8 text-center sm:w-fit w-full font-semibold text-white transition-all hover:bg-blue-800"
											>
											<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 32 32"><path fill="currentColor" d="M11.61 29.92a1 1 0 0 1-.6-1.07L12.83 17H8a1 1 0 0 1-1-1.23l3-13A1 1 0 0 1 11 2h10a1 1 0 0 1 .78.37a1 1 0 0 1 .2.85L20.25 11H25a1 1 0 0 1 .9.56a1 1 0 0 1-.11 1l-13 17A1 1 0 0 1 12 30a1.1 1.1 0 0 1-.39-.08M17.75 13l2-9H11.8L9.26 15h5.91l-1.59 10.28L23 13Z"/></svg>
											Hızlı Tevkil Oluştur
										</Link>
									</>
								) : (
									<Link
										href="/gorevler/liste"
										className="flex items-center gap-2 rounded-full bg-indigo-600 py-3 px-8 text-center sm:w-fit w-full font-semibold text-white transition-all hover:bg-indigo-800"
									>
										<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
											<path 
												fill="none" 
												stroke="currentColor" 
												strokeLinecap="round" 
												strokeLinejoin="round" 
												strokeWidth="1.5" 
												d="M5.08 15.296c-1.218.738-4.412 2.243-2.466 4.126c.95.92 2.009 1.578 3.34 1.578h7.593c1.33 0 2.389-.658 3.34-1.578c1.945-1.883-1.25-3.389-2.468-4.126a9.06 9.06 0 0 0-9.338 0M13.5 7a4 4 0 1 1-8 0a4 4 0 0 1 8 0M17 5h5m-5 3h5m-2 3h2" 
												color="currentColor"
											/>
										</svg>
										Aktif Görevler
									</Link>
								)}
								</div>
							<div
								className="flex sm:space-x-4 sm:flex-row mt-4 flex-col items-center w-full sm:gap-0 sm:items-start sm:justify-normal gap-4 justify-center">
							
								<Link
									href="/tevkilapp-nasil-calisir"
									className="flex items-center gap-2 rounded-full bg-gray-600 py-3 px-8 text-center sm:w-fit w-full font-semibold text-white transition-all hover:bg-gray-800 hover:text-white"
								>
									<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 16 16"><path fill="currentColor" d="m10.878.282l.348 1.071a2.2 2.2 0 0 0 1.398 1.397l1.072.348l.021.006a.423.423 0 0 1 0 .798l-1.071.348a2.2 2.2 0 0 0-1.399 1.397l-.348 1.07a.423.423 0 0 1-.798 0l-.348-1.07a2.2 2.2 0 0 0-1.399-1.403l-1.072-.348a.423.423 0 0 1 0-.798l1.072-.348a2.2 2.2 0 0 0 1.377-1.397l.348-1.07a.423.423 0 0 1 .799 0m4.905 7.931l-.765-.248a1.58 1.58 0 0 1-1-.999l-.248-.764a.302.302 0 0 0-.57 0l-.25.764a1.58 1.58 0 0 1-.983.999l-.765.248a.303.303 0 0 0 0 .57l.765.249a1.58 1.58 0 0 1 1 1.002l.248.764a.302.302 0 0 0 .57 0l.249-.764a1.58 1.58 0 0 1 .999-.999l.765-.248a.303.303 0 0 0 0-.57zm-3.027 3.557c.219.149.477.229.746.23q.13 0 .256-.018a7 7 0 1 1-4.976-10.94c-.06.18-.16.34-.29.47s-.29.24-.45.29l-.736.237a6.001 6.001 0 1 0 5.396 9.688zM7.44 5.003l.593.196c.15.05.29.13.47.29c.074.074.138.156.2.271a.75.75 0 1 1-1.263-.757M7.999 7a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-1 0v-3a.5.5 0 0 1 .5-.5"/></svg>
									Detaylı Bilgi
								</Link>
							</div>

						</div>

						{/* <!-- Hero image --> */}
						<div className="sm:col-span-6 col-span-12">
							<div className="relative text-center lg:pl-32 lg:text-right">

								{
									currentIndex % 3 === 0 && (
								<div
									className="absolute left-[5%] bottom-10 inline-block animate-fly rounded-2xl bg-white p-6 shadow-2xl sm:left-[15%] md:left-20 z-10">
									<div className="flex gap-4">
										<div className="text-left">
											<span className="block font-display text-3xl text-emerald-600">
												+16.2M ₺
											</span>
											<span className="block font-display text-sm text-gray-600">
												Yıllık Tevkil Kazanç Cirosu
											</span>
										</div>
									</div>
								</div>
									)
								}

								{
									currentIndex % 3 === 1 && (
								<div
									className="absolute left-[5%] top-10 inline-block animate-fly rounded-2xl bg-white p-6 shadow-2xl sm:left-[15%] md:left-20 z-10">
									<div className="flex gap-4">
										<div className="text-left">
											<span className="block font-display text-3xl text-cyan-600">
												81 İl
											</span>
											<span className="block font-display text-sm text-gray-600">
												Türkiye&apos;nin her yerinden avukatlar
											</span>
										</div>
									</div>
								</div>
									)
								}

								{
									currentIndex % 3 === 2 && (
								<div
									className="absolute left-[5%] top-1/2 inline-block animate-fly rounded-2xl bg-white p-6 shadow-2xl sm:left-[15%] md:left-20 z-10">
									<div className="flex gap-4">
										<div className="text-left">
											<span className="block font-display text-3xl text-blue-500">
												3 dk.
											</span>
											<span className="block font-display text-sm text-gray-600">
												Tevkil yayınlamak için<br /> harcamanız gereken süre
											</span>
										</div>
									</div>
								</div>
									)
								}

								<div className="relative">
									<Image
										width={524}
										height={670}
										src={currentContent.image}
										alt="crypto consultant hero"
										className="inline-block rounded-2.5xl"
									/>
									<div className="absolute bottom-5 h-1 bg-white/30 left-[15%] w-[80%] rounded-full">
										<div 
											className="h-1 bg-white/60 transition-all duration-100 ease-linear rounded-full"
											style={{ width: `${progress}%` }}
										/>
									</div>
								</div>

								{ currentIndex % 2 === 0 && (
								<div className="absolute bottom-2/3 right-[5%] inline-block animate-fly rounded-2xl bg-white p-8 shadow-2xl sm:right-[5%] lg:-right-[17%]">
									<div className="text-left">
										<span className="block font-display text-3xl text-lime-800">
										+10bin
										</span>
										<span className="mb-0 block font-display text-sm text-jacarta-600">
										Başarılı Tevkil Görevi
										</span>
									</div>
								</div>
								)
								}

								{ currentIndex % 2 === 1 && (
								<div className="absolute top-2/3 right-[5%] inline-block animate-fly rounded-2xl bg-white p-8 shadow-2xl sm:right-[5%] lg:-right-[17%]">
									<div className="text-left">
										<span className="block font-display text-3xl text-[#737EF2]">
										+20bin
										</span>
										<span className="mb-5 block font-display text-sm text-jacarta-600">
										Kayıtlı avukat
										</span>
										<Image
											width={152}
											height={24}
											src="https://cdn.tevkilapp.com/images/crypto-consultant/happy_customers.png"
											alt="happy customers"
										/>
									</div>
								</div>
								)
								}
							</div>
						</div>
					</div>
				</div>
			</section>
			{/* <!-- end hero --> */}			
		</>
	);
};

export default Hero_7;
