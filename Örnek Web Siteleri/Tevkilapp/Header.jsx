import Image from 'next/image';
import Link from 'next/link';
import DarkMode from '../mode/DarkMode';
import Logo from './../../public/tevkilapp-color-logo.png';
import WhiteLogo from './../../public/tevkilapp-white-logo.png';
import React, {useEffect, useState} from 'react';
import {useSelector, useDispatch} from 'react-redux';
import {UserNotLoggedIn} from '@/container/header/dropdown/UserNotLoggedIn';
import {UserLoggedInDropdown} from '@/container/header/dropdown/UserLoggedInDropdown';
import NotificationDropdown from '@/container/header/dropdown/NotificationDropdown';
import {UserAuthDropdown} from '@/container/header/dropdown/UserAuthDropdown';
import {useRouter} from 'next/router';
import {BsCardChecklist, BsDoorOpen, BsLifePreserver, BsPersonAdd, BsPersonGear, BsPlusLg, BsReceipt, BsStar, BsGeoAlt, BsHouse} from 'react-icons/bs';
import {logout} from '../../redux/slices/userSlice';
import Cookies from 'js-cookie';
import request from '@/utils/request';
import Swal from 'sweetalert2';
import NotificationMobile from '@/container/header/dropdown/NotificationMobile';
import { setNotifications, setLoading, setError } from '../../redux/slices/notificationSlice';

export default function Header() {
	const router = useRouter();
	const user = useSelector(state => state.user);
	const [queueList, setQueueList] = useState([]);
	const [locations, setLocations] = useState([]);
	const [toggle, setToggle] = useState(false);
	const [showNav, setShowNav] = useState(false);
	const [isLogged, setLogged] = useState(false);
	const [mobileUserDropdown, setMobileUserDropdown] = useState(false);
	const [showLocationModal, setShowLocationModal] = useState(false);
	const [searchTerm, setSearchTerm] = useState('');
	const [selectedLocations, setSelectedLocations] = useState([]);
	const [alreadySelectedLocations, setAlreadySelectedLocations] = useState([]);
	const [showBaroCardAlert, setShowBaroCardAlert] = useState(false);
	const dispatch = useDispatch();
	const notifications = useSelector(state => state.notifications.notifications);
	const loading = useSelector(state => state.notifications.loading);
	const error = useSelector(state => state.notifications.error);


	// Bildirimleri kontrol et ve güncelle
	const checkAndUpdateNotifications = async () => {
		console.log(isLogged);
		// if (!isLogged) return;

		const lastFetchTime = localStorage.getItem('notificationsLastFetch');
		const currentTime = new Date().getTime();
		const tenMinutes = 10 * 60 * 1000; // 10 dakika (milisaniye cinsinden)

		// Eğer son çekme zamanı yoksa veya 10 dakikadan eskiyse
		if (!lastFetchTime || (currentTime - parseInt(lastFetchTime)) > tenMinutes) {
			try {
				dispatch(setLoading(true));
				const response = await request('/user/notifications', 'GET', null, true);

				if (response && response.success && Array.isArray(response.data)) {
					
					const formattedNotifications = response.data.map(notification => {
						return {
							id: notification.id || Math.random().toString(36).substr(2, 9),
							title: notification.title || 'Bildirim',
							message: notification.message || '',
							read: notification.read || false,
							link: notification.link || null, 
							icon: notification.icon || 'default',
							submessage: notification.submessage || null
						};
					});
										
					// Redux state'ini güncelle
					dispatch(setNotifications(formattedNotifications));
					
					// LocalStorage'a kaydet
					localStorage.setItem('notifications', JSON.stringify(formattedNotifications));
					localStorage.setItem('notificationsLastFetch', currentTime.toString());
					
				} else {
					dispatch(setError('API yanıtı geçersiz format'));
				}
			} catch (error) {
				console.error('Bildirimler alınamadı:', error);
				dispatch(setError(error.message));
				// Hata durumunda localStorage'dan eski bildirimleri yükle
				const storedNotifications = localStorage.getItem('notifications');
				if (storedNotifications) {
					console.log('Hata durumunda localStorage\'dan bildirimler yükleniyor...');
					dispatch(setNotifications(JSON.parse(storedNotifications)));
				}
			} finally {
				dispatch(setLoading(false));
			}
		} else {
			// LocalStorage'dan bildirimleri al
			const storedNotifications = localStorage.getItem('notifications');
			if (storedNotifications) {
				dispatch(setNotifications(JSON.parse(storedNotifications)));
			}
		}
	};

	useEffect(() => {
		if (user.user) {
			setLogged(true);
			checkAndUpdateNotifications();
		}
	}, [user.user]);

	useEffect(() => {
		const userData = localStorage.getItem('user');
		if (userData) {
			const parsedUser = JSON.parse(userData);
			setShowBaroCardAlert(!parsedUser.user_verify_at);
		}
	}, []);

	const filteredLocations = locations.filter(location =>
		!selectedLocations.some(selected => selected.id === location.id) &&
		(location.name.toLocaleLowerCase('tr-TR').includes(searchTerm.toLocaleLowerCase('tr-TR')) ||
		location.city.toLocaleLowerCase('tr-TR').includes(searchTerm.toLocaleLowerCase('tr-TR')))
	);

	const handleLocationSelect = (location) => {
		if (selectedLocations.length < 50) {
			setSelectedLocations([...selectedLocations, location]);
		}
	};

	const handleLocationRemove = (locationId) => {
		setSelectedLocations(selectedLocations.filter(loc => loc.id !== locationId));
	};

	useEffect(() => {
		// API'den önceden seçilmiş lokasyonları çek
		// Şimdilik örnek veri kullanıyoruz
		setSelectedLocations(alreadySelectedLocations);
	}, []);

	useEffect(() => {
		if (router.pathname.startsWith('/uyelik')) {
			setShowNav(false);
		}
		else {
			setShowNav(true);
		}
	}, [router]);

	useEffect(() => {
		window.addEventListener('resize', () => {
			if (window.innerWidth >= 1024) {
				setToggle(false);
			}
		});
	}, []);

	useEffect(() => {
		const getMyLocations = async () => {
			const response = await request('/queue/my-list', 'GET', null, true);
			if (response.success) {
				setAlreadySelectedLocations(response.data);
				setSelectedLocations(response.data);
			}
		};
		

		const fetchQueueList = async () => {
			// localStorage'da queueList var mı kontrol et
			const cachedQueueList = localStorage.getItem('queueList');
			if (cachedQueueList) {
				const parsedData = JSON.parse(cachedQueueList);
				setQueueList(parsedData);
				
				const districts = parsedData.districts.map(item => ({
					id: "ilce-" + item.id,
					name: item.name,
					type: 'İlçe',
					city: item.city.name
				}));

				const courthouses = parsedData.courthouses.map(item => ({
					id: "adliye-" + item.id,
					name: item.name,
					type: 'Adliye',
					city: item.city.name
				}));

				setLocations([...districts, ...courthouses]);
				getMyLocations();
				return;
			}

			try {
				const response = await request('/queue/all-list', 'GET', null, true);
				if (response.success) {
					setQueueList(response.data);
					
					const districts = response.data.districts.map(item => ({
						id: "ilce-" + item.id,
						name: item.name,
						type: 'İlçe',
						city: item.city.name
					}));

					const courthouses = response.data.courthouses.map(item => ({
						id: "adliye-" + item.id,
						name: item.name,
						type: 'Adliye',
						city: item.city.name
					}));

					setLocations([...districts, ...courthouses]);
					getMyLocations();
					localStorage.setItem('queueList', JSON.stringify(response.data));
				}
			} catch (error) {
				console.error('Kuyruk listesi alınamadı:', error);
			}
		};

		if (user.user) {
			fetchQueueList();
		}
	}, [user.user]);

	const handleLogout = async () => {
		const result = await Swal.fire({
			title: 'Çıkış yapmak istediğinize emin misiniz?',
			text: 'Oturumunuz sonlandırılacak.',
			icon: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Evet, çıkış yap',
			cancelButtonText: 'İptal'
		});

		if (result.isConfirmed) {
			dispatch(logout());
			Cookies.remove('userToken');
			Cookies.remove('user');
			route.push('/');
			
			await Swal.fire({
				title: 'Çıkış Yapıldı!',
				text: 'Başarıyla çıkış yaptınız.',
				icon: 'success',
				timer: 1500,
				showConfirmButton: false
			});
		}
	};

	const handleSaveLocations = async () => {
		try {
			const response = await request('/queue/save-my-list', 'POST', {
				locations: selectedLocations.map(location => location.id
				)
			}, true);

			if (response.success) {
				// Başarılı kayıt sonrası modalı kapat
				//setShowLocationModal(false);
				// Başarılı mesajı göster
				Swal.fire({
					title: 'Başarılı!',
					text: 'Görev yerleriniz başarıyla kaydedildi.',
					icon: 'success',
					timer: 1500,
					showConfirmButton: false
				});
			} else {
				// Hata durumunda kullanıcıya bilgi ver
				Swal.fire({
					title: 'Hata!',
					text: 'Görev yerleriniz kaydedilirken bir hata oluştu.',
					icon: 'error',
					confirmButtonText: 'Tamam'
				});
			}
		} catch (error) {
			console.error('Görev yerleri kaydedilirken hata:', error);
			Swal.fire({
				title: 'Hata!',
				text: 'Görev yerleriniz kaydedilirken bir hata oluştu.',
				icon: 'error',
				confirmButtonText: 'Tamam'
			});
		}
	};

	return (
		(showNav ? (
			<>
				{/* main dropdown menu sart*/}
				<header
					className="js-page-header absolute sm:fixed top-0 z-20 w-full backdrop-blur transition-colors dark:bg-none">
					<div className="flex justify-center sm:justify-start items-center py-6 ml-auto mr-auto h-full max-w-[91rem] px-4 ">
						<Link className="shrink-0" href="/">
							<div className="dark:hidden">
								<Image
									src={Logo}
									style={{height: 'auto', width: '170px'}}
									alt="TevkilApp | Avukatlar arası görev paylaşım platformu"
								/>
							</div>
							<div className="hidden dark:block">
								<Image
									src={WhiteLogo}
									style={{height: 'auto', width: '170px'}}
									alt="TevkilApp | Avukatlar arası görev paylaşım platformu"
								/>
							</div>
						</Link>
						{/* End  logo */}


						{/* ... rest of the existing code ... */}

						<div
							className="js-mobile-menu dark:bg-jacarta-800 invisible fixed inset-0 z-10 ml-auto items-center bg-white opacity-0 lg:visible lg:relative lg:inset-auto lg:flex lg:bg-transparent lg:opacity-100 dark:lg:bg-transparent">
							<nav className="navbar w-full">
								<ul className="flex flex-col lg:flex-row">

									{isLogged ? (<li className="group">
										<Link href="/gorevler/liste" className="user-login-menu-link">
											<button className="flex justify-center items-center gap-2 text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center justify-between py-3.5 text-base dark:text-white lg:px-5">
											<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 16 16"><path fill="currentColor" fillRule="evenodd" d="m13.6 12.186l-1.357-1.358c-.025-.025-.058-.034-.084-.056c.53-.794.84-1.746.84-2.773a5 5 0 0 0-.84-2.772c.026-.02.059-.03.084-.056L13.6 3.813a6.96 6.96 0 0 1 0 8.373M8 15a6.96 6.96 0 0 1-4.186-1.4l1.358-1.358c.025-.025.034-.057.055-.084C6.02 12.688 6.974 13 8 13a5 5 0 0 0 2.773-.84c.02.026.03.058.056.083l1.357 1.358A6.96 6.96 0 0 1 8 15m-5.601-2.813a6.96 6.96 0 0 1 0-8.373l1.359 1.358c.024.025.057.035.084.056A4.97 4.97 0 0 0 3 8c0 1.027.31 1.98.842 2.773c-.027.022-.06.031-.084.056zm5.6-.187A4 4 0 1 1 8 4a4 4 0 0 1 0 8M8 1c1.573 0 3.019.525 4.187 1.4L10.83 3.758c-.025.025-.035.057-.056.084A5 5 0 0 0 8 3a5 5 0 0 0-2.773.842c-.021-.027-.03-.059-.055-.084L3.814 2.4A6.96 6.96 0 0 1 8 1m0-1a8.001 8.001 0 1 0 .003 16.002A8.001 8.001 0 0 0 8 0"/></svg>
												<span> Aktif Görevler</span>
											</button>
										</Link>
									</li>) : (<span className="hidden-style"></span>)}

									{/* home */}
									<li className="group">
										<Link href="/tevkilapp-nasil-calisir">
											<button className="flex justify-center items-center gap-2 text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center justify-between py-3.5 text-base dark:text-white lg:px-5">
											<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"><path d="M14.69 18.498c-.508.21-.885.65-1.015 1.185c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 0 0-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 0 0-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 0 0 1.066-2.573c-.94-1.543.826-3.31 2.37-2.37c1 .608 2.296.07 2.572-1.065c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 0 0 2.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 0 0 1.065 2.572a1.67 1.67 0 0 1 1.179.982"/><path d="M14.95 12.553a3 3 0 1 0-1.211 1.892M19 22v.01M19 19a2.003 2.003 0 0 0 .914-3.782a1.98 1.98 0 0 0-2.414.483"/></g></svg>
												<span>Nasıl Çalışır?</span>
											</button>
										</Link>
									</li>

									<li className="js-nav-dropdown nav-item dropdown group relative">
										<Link href="/hakkimizda">
											<button className="flex justify-center items-center gap-2 dropdown-toggle text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center justify-between py-3.5 text-base dark:text-white lg:px-5 w-full">
											<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"><path fill="currentColor" d="M18 15h-2v2h2m0-6h-2v2h2m2 6h-8v-2h2v-2h-2v-2h2v-2h-2V9h8M10 7H8V5h2m0 6H8V9h2m0 6H8v-2h2m0 6H8v-2h2M6 7H4V5h2m0 6H4V9h2m0 6H4v-2h2m0 6H4v-2h2m6-10V3H2v18h20V7z"/></svg>
												<span>Hakkımızda</span>
												<i className="lg:hidden">
													<svg
														xmlns="http://www.w3.org/2000/svg"
														viewBox="0 0 24 24"
														width={24}
														height={24}
														className="h-4 w-4 dark:fill-white"
													>
														<path fill="none" d="M0 0h24v24H0z"/>
														<path
															d="M12 13.172l4.95-4.95 1.414 1.414L12 16 5.636 9.636 7.05 8.222z"/>
													</svg>
												</i>
											</button>
										</Link>
									</li>

									{/* resource */}
									{/* <li className="js-nav-dropdown group relative" onClick={() => setToggle(false)}>
										<Link href="/iletisim">
											<button className="dropdown-toggle text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center justify-between py-3.5 text-base dark:text-white lg:px-5 w-full">
												<span>İletişim</span>
												<i className="lg:hidden">
													<svg
														xmlns="http://www.w3.org/2000/svg"
														viewBox="0 0 24 24"
														width={24}
														height={24}
														className="h-4 w-4 dark:fill-white"
													>
														<path fill="none" d="M0 0h24v24H0z"/>
														<path
															d="M12 13.172l4.95-4.95 1.414 1.414L12 16 5.636 9.636 7.05 8.222z"/>
													</svg>
												</i>
											</button>
										</Link>
									</li> */}

									{/* create */}

									<li className="group">
										<Link href="/sss">
											<button className="flex justify-center items-center gap-2 text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center justify-between py-3.5 text-base dark:text-white lg:px-5">
											<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 16 16"><path fill="currentColor" fillRule="evenodd" d="m13.6 12.186l-1.357-1.358c-.025-.025-.058-.034-.084-.056c.53-.794.84-1.746.84-2.773a5 5 0 0 0-.84-2.772c.026-.02.059-.03.084-.056L13.6 3.813a6.96 6.96 0 0 1 0 8.373M8 15a6.96 6.96 0 0 1-4.186-1.4l1.358-1.358c.025-.025.034-.057.055-.084C6.02 12.688 6.974 13 8 13a5 5 0 0 0 2.773-.84c.02.026.03.058.056.083l1.357 1.358A6.96 6.96 0 0 1 8 15m-5.601-2.813a6.96 6.96 0 0 1 0-8.373l1.359 1.358c.024.025.057.035.084.056A4.97 4.97 0 0 0 3 8c0 1.027.31 1.98.842 2.773c-.027.022-.06.031-.084.056zm5.6-.187A4 4 0 1 1 8 4a4 4 0 0 1 0 8M8 1c1.573 0 3.019.525 4.187 1.4L10.83 3.758c-.025.025-.035.057-.056.084A5 5 0 0 0 8 3a5 5 0 0 0-2.773.842c-.021-.027-.03-.059-.055-.084L3.814 2.4A6.96 6.96 0 0 1 8 1m0-1a8.001 8.001 0 1 0 .003 16.002A8.001 8.001 0 0 0 8 0"/></svg>
												<span> S.S.S.</span>
											</button>
										</Link>
									</li>

									<li className="group ml-4 mr-3">
										<Link href={isLogged ? "/gorevler/olustur" : "/gorev-olustur"}>
											<button className="flex justify-center items-center gap-2 px-8 py-3 bg-indigo-400/30 hover:shadow-lg hover:shadow-indigo-400/30 rounded-full text-indigo-800 font-display hover:bg-indigo-500 hover:text-white dark:hover:text-accent flex items-center justify-between py-3.5 text-base dark:text-white lg:px-5">
												<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="-0.5 -0.5 24 24"><path fill="currentColor" d="m21.289.98l.59.59c.813.814.69 2.257-.277 3.223L9.435 16.96l-3.942 1.442c-.495.182-.977-.054-1.075-.525a.93.93 0 0 1 .045-.51l1.47-3.976L18.066 1.257c.967-.966 2.41-1.09 3.223-.276zM8.904 2.19a1 1 0 1 1 0 2h-4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4a1 1 0 0 1 2 0v4a4 4 0 0 1-4 4h-12a4 4 0 0 1-4-4v-12a4 4 0 0 1 4-4z"/></svg>
												<span>Tevkil Oluştur</span>
											</button>
										</Link>
									</li>

									
									
									<li className="group">
									{isLogged ? (
											<UserLoggedInDropdown mobileUserDropdown={mobileUserDropdown} setMobileUserDropdown={setMobileUserDropdown} user={user.user} setShowLocationModal={setShowLocationModal} />
									) : (
										<Link href="/login">
											<button className="flex justify-center items-center gap-2 px-8 py-3 bg-blue-400/30 hover:shadow-lg hover:shadow-blue-400/30 rounded-full text-blue-800 font-display hover:bg-blue-500 hover:text-white dark:hover:text-accent flex items-center justify-between py-3.5 text-base dark:text-white lg:px-5">
											<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 256 256"><path fill="currentColor" d="M230.93 220a8 8 0 0 1-6.93 4H32a8 8 0 0 1-6.92-12c15.23-26.33 38.7-45.21 66.09-54.16a72 72 0 1 1 73.66 0c27.39 8.95 50.86 27.83 66.09 54.16a8 8 0 0 1 .01 8"/></svg>
												<span>Giriş Yap</span>
											</button>
										</Link>
									)}										
									</li>

									<li className="group">
									{isLogged ? (
										<NotificationDropdown notifications={notifications} setNotifications={setNotifications} setShowLocationModal={setShowLocationModal} />
									) : (
										<></>
									)}										
									</li>
								</ul>
							</nav>
							{/* End menu for dropdown */}

							{/* End header right content (metamask and other) for dropdown */}
						</div>
						{/* header menu conent end for dropdown */}

						{/*mobile taraflı user dropdown kısmı*/}
						{/*
						<div className="ml-auto flex relative lg:hidden">
							<div className="">
								<button
									onClick={() => setMobileUserDropdown(!mobileUserDropdown)}
									
									className={`absolute !right-24 border-jacarta-100 ${mobileUserDropdown ? 'bg-accent dark:bg-accent border-transparent' : 'dark:bg-white/[.15]  bg-white '} group ml-2 flex h-10 w-10 items-center justify-center rounded-full border  transition-colors  dark:border-transparent `}>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										viewBox="0 0 24 24"
										width={24}
										height={24}
										className={` h-4 w-4 transition-colors  ${mobileUserDropdown ? 'fill-white  ' : 'fill-jacarta-700 dark:fill-white'}`}
									>
										<path fill="none" d="M0 0h24v24H0z"/>
										<path d="M11 14.062V20h2v-5.938c3.946.492 7 3.858 7 7.938H4a8.001 8.001 0 0 1 7-7.938zM12 13c-3.315 0-6-2.685-6-6s2.685-6 6-6 6 2.685 6 6-2.685 6-6 6z"/>
									</svg>
								</button>
								<div
									style={{display: mobileUserDropdown ? 'block' : 'none'}}
									className="dark:bg-jacarta-800 mt-5 pt-4 pb-4 !right-14 absolute !top-[85%] !left-auto z-10 min-w-[16rem] whitespace-nowrap rounded-xl bg-white transition-all will-change-transform before:absolute before:-top-3 before:h-3 before:w-full lg:absolute lg:grid lg:!translate-y-4 lg:py-4 lg:px-2 lg:shadow-2xl">
									{isLogged ? (<UserLoggedInDropdown mobileUserDropdown={mobileUserDropdown} setMobileUserDropdown={setMobileUserDropdown} user={user.user}/>) : (<UserNotLoggedIn/>)}

								</div>
							</div>


							<button
								className="js-mobile-toggle border-jacarta-100 hover:bg-accent dark:hover:bg-accent focus:bg-accent group ml-2 flex h-10 w-10 items-center justify-center rounded-full border bg-white transition-colors hover:border-transparent focus:border-transparent dark:border-transparent dark:bg-white/[.15]"
								aria-label="open mobile menu"
								onClick={() => setToggle(true)}
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 24 24"
									width={24}
									height={24}
									className="fill-jacarta-700 h-4 w-4 transition-colors group-hover:fill-white group-focus:fill-white dark:fill-white"
								>
									<path fill="none" d="M0 0h24v24H0z"/>
									<path d="M18 18v2H6v-2h12zm3-7v2H3v-2h18zm-3-7v2H6V4h12z"/>
								</svg>
							</button>

						</div>
						*/}
						{/* End header right content  for mobile */}
					</div>
					{/* End flex item */}
				</header>
				{/* main dropdown menu end */}

				{/* start mobile menu and it's other materials  */}
				<div className={`lg:hidden js-mobile-menu dark:bg-jacarta-800 invisible fixed inset-0 z-20 ml-auto items-center bg-white opacity-0 lg:visible lg:relative lg:inset-auto lg:bg-transparent lg:opacity-100 dark:lg:bg-transparent ${toggle ? 'nav-menu--is-open' : 'hidden'}`}>
					<div className="t-0 dark:bg-jacarta-800 fixed left-0 z-10 flex w-full items-center justify-between bg-white p-6 lg:hidden">
						<div className="dark:hidden">
							<Image
								src={Logo}
								height={28}
								width={130}
								alt="TevkilApp - İşlerinizi Kolaylaştırın, Sonuçları Hızlandırın, Hukuki Yükümlülükleri TevkilApp İle Sorunsuz Yönetin!"
								className="max-h-7 h-auto object-cover" 
							/>
						</div>

						<div className="hidden dark:block">
							<Image
								src={WhiteLogo}
								height={28}
								width={130}
								alt="TevkilApp - İşlerinizi Kolaylaştırın, Sonuçları Hızlandırın, Hukuki Yükümlülükleri TevkilApp İle Sorunsuz Yönetin!"
							/>
						</div>

						<button
							className="js-mobile-close border-jacarta-100 hover:bg-accent focus:bg-accent group dark:hover:bg-accent ml-2 flex h-10 w-10 items-center justify-center rounded-full border bg-white transition-colors hover:border-transparent focus:border-transparent dark:border-transparent dark:bg-white/[.15]"
							onClick={() => setToggle(false)}
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								width={24}
								height={24}
								className="fill-jacarta-700 h-4 w-4 transition-colors group-hover:fill-white group-focus:fill-white dark:fill-white"
							>
								<path fill="none" d="M0 0h24v24H0z"/>
								<path d="M12 10.586l4.95-4.95 1.414 1.414-4.95 4.95 4.95 4.95-1.414 1.414-4.95-4.95-4.95 4.95-1.414-1.414 4.95-4.95-4.95-4.95L7.05 5.636z"/>
							</svg>
						</button>
					</div>

					<nav className="navbar hidden lg:block w-full">
						<ul className="flex flex-col lg:flex-row" style={{marginTop: '5rem'}}>
							{user.user && (
								<li className="js-nav-dropdown group relative" onClick={() => setToggle(false)}>
									<Link href="/gorevler/liste">
										<button onClick={() => setToggle(false)} className="text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center justify-between py-3.5 text-base dark:text-white lg:px-5">
											<span>Aktif Görevler</span>
										</button>
									</Link>
								</li>
							)}
							<li className="js-nav-dropdown group relative" onClick={() => setToggle(false)}>
								<Link href="/">
									<button
										onClick={() => setToggle(false)}
										className="dropdown-toggle text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center justify-between py-3.5 text-base dark:text-white lg:px-5 w-full"
									>
										<span>Anasayfa</span>
									</button>
								</Link>
							</li>
							<li className="js-nav-dropdown nav-item dropdown group relative">
								<Link href="/hakkimizda">
									<button
										onClick={() => setToggle(false)}
										className="dropdown-toggle text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center justify-between py-3.5 text-base dark:text-white lg:px-5 w-full"
									>
										<span>Hakkımızda</span>
									</button>
								</Link>
							</li>
							<li className="js-nav-dropdown group relative" onClick={() => setToggle(false)}>
								<Link href="/iletisim">
									<button
										onClick={() => setToggle(false)}
										className="dropdown-toggle text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center justify-between py-3.5 text-base dark:text-white lg:px-5 w-full"
									>
										<span>İletişim</span>
									</button>
								</Link>
							</li>
							<li className="group" onClick={() => setToggle(false)}>
								<Link href="/tevkilapp-nasil-calisir">
									<button
										onClick={() => setToggle(false)}
										className="text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center justify-between py-3.5 text-base dark:text-white lg:px-5">
										<span>Nasıl Çalışır?</span>
									</button>
								</Link>
							</li>

							<li className="group" onClick={() => setToggle(false)}>
								<Link href="/sss">
									<button
										className="text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center justify-between py-3.5 text-base dark:text-white lg:px-5">
										<span>SSS</span>
									</button>
								</Link>
							</li>
						</ul>
					</nav>
					{/* End navbar mobile menu  */}

					<div className="w-full lg:hidden pb-20 pt-20 mt-4">
						<div className="flex flex-col">
						{user.user && (
							<>
								<div className="flex flex-row bg-gray-100 p-3 rounded-lg align-middle gap-3 mt-0 items-center dark:bg-jacarta-900">
									<Image src={`https://cdn.tevkilapp.com/${user.user.avatar}`}
												style={{height: 'auto', width: 'auto'}}
												height={50}
												alt="avatar"
												width={50}
												quality={90}
												className="rounded-lg max-h-[60px]"/>
									<div>
										<div className="font-display font-semibold text-sm text-three-dot-mobile sm:text-three-dot -mb-1"
												style={{height: '18px'}}>
											{user.user.full_name}
										</div>

										<span className="text-sm">Avukat</span>
									</div>
								</div>
							</>
						)}

						<div className="grid grid-cols-3 gap-3 mt-4">
						{user.user && (
							<div className="js-nav-dropdown group relative bg-gray-100/50 rounded-lg text-center flex items-center justify-center" onClick={() => setToggle(false)}>
								<Link
									href="/premium"
									className="flex justify-center items-center flex-col text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center gap-4 py-3.5 text-base dark:text-white lg:px-5">
									<BsStar className="text-2xl"></BsStar>
									<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Premium Üyelik</span>
								</Link>
							</div>
						)}
										<div className="js-nav-dropdown group relative bg-gray-100/50 rounded-lg text-center flex items-center justify-center" onClick={() => setToggle(false)}>
											<Link
												href="/"
												className="flex justify-center items-center flex-col text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center gap-4 py-3.5 text-base dark:text-white lg:px-5">
												<BsHouse className="text-2xl"></BsHouse>
												<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Anasayfa</span>
											</Link>
										</div>
										<div className="js-nav-dropdown group relative bg-gray-100/50 rounded-lg text-center flex items-center justify-center" onClick={() => setToggle(false)}>
											<Link
												href="/tevkilapp-nasil-calisir"
												className="flex justify-center items-center flex-col text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center gap-4 py-3.5 text-base dark:text-white lg:px-5">
												<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5"><path strokeLinejoin="round" d="m15 18.5l5-5m0 5l-5-5"/><path d="M11 14H3m8 4H3M3 6h10.5M20 6h-2.25M20 10H9.5M3 10h2.25"/></g></svg>
												<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Nasıl Çalışır?</span>
											</Link>
										</div>
										<div className="js-nav-dropdown group relative bg-gray-100/50 rounded-lg text-center flex items-center justify-center" onClick={() => setToggle(false)}>
											<Link
												href="/gorevler/olustur"
												className="flex justify-center items-center flex-col text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center gap-4 py-3.5 text-base dark:text-white lg:px-5"
											>
												<BsPlusLg className="text-2xl"></BsPlusLg>
												<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Tevkil Oluştur</span>
											</Link>
										</div>
								{user.user && (
									<>
										<div className="js-nav-dropdown group relative bg-gray-100/50 rounded-lg text-center flex items-center justify-center" onClick={() => setToggle(false)}>
											<Link
												href="/gorevler/gorevlerim"
												className="flex justify-center items-center flex-col text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center gap-4 py-3.5 text-base dark:text-white lg:px-5"
											>
												<BsReceipt className="text-2xl"></BsReceipt>
												<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Oluşturduğum Görevler</span>
											</Link>
										</div>
										<div className="js-nav-dropdown group relative bg-gray-100/50 rounded-lg text-center flex items-center justify-center" onClick={() => setToggle(false)}>
											<Link
												href="/gorevler/katildiklarim"
												className="flex justify-center items-center flex-col text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center gap-4 py-3.5 text-base dark:text-white lg:px-5"
											>
												<BsCardChecklist className="text-2xl"></BsCardChecklist>
												<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Başvurduğum Görevler</span>
											</Link>
										</div>

										{/* <div className="js-nav-dropdown group relative bg-gray-100/50 rounded-lg text-center flex items-center justify-center" onClick={() => setToggle(false)}>
											<Link
												href="/sira"
												className="flex justify-center items-center flex-col text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center gap-4 py-3.5 text-base dark:text-white lg:px-5"
											>
												<HiQueueList className="text-2xl"></HiQueueList>
												<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Görev Sıralarım</span>
											</Link>
										</div> */}
										<div className="js-nav-dropdown group relative bg-gray-100/50 rounded-lg text-center flex items-center justify-center" onClick={() => setToggle(false)}>
											<div
												onClick={() => {
													setShowLocationModal(true);
													setMobileUserDropdown(false);
												}}
												className="flex justify-center items-center flex-col text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center gap-4 py-3.5 text-base dark:text-white lg:px-5"
											>
												<BsGeoAlt className="text-2xl"></BsGeoAlt>
												<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Görev Yerlerim</span>
											</div>
										</div>
										<div className="js-nav-dropdown group relative bg-gray-100/50 rounded-lg text-center flex items-center justify-center" onClick={() => setToggle(false)}>
											<Link
												href="/ayarlar/avatar-degistir"
												className="flex justify-center items-center flex-col text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center gap-4 py-3.5 text-base dark:text-white lg:px-5"
											>
												<BsPersonGear className="text-2xl"></BsPersonGear>
												<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Ayarlarım</span>
											</Link>
										</div>
										<div className="js-nav-dropdown group relative bg-gray-100/50 rounded-lg text-center flex items-center justify-center" onClick={() => setToggle(false)}>
											<Link
												href="/destek/liste"
												className="flex justify-center items-center flex-col text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center gap-4 py-3.5 text-base dark:text-white lg:px-5"
											>
												<BsLifePreserver className="text-2xl"></BsLifePreserver>
												<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Destek Sistemi</span>
											</Link>
										</div>
									</>
								)}
										<div className="js-nav-dropdown group relative bg-gray-100/50 rounded-lg text-center flex items-center justify-center" onClick={() => setToggle(false)}>
											<Link
												href="/sss"
												className="flex justify-center items-center flex-col text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center gap-4 py-3.5 text-base dark:text-white lg:px-5"
											>
												<svg xmlns="http://www.w3.org/2000/svg" width={28} height={28} viewBox="0 0 24 24"><path fill="currentColor" d="M18 15H6l-4 4V3a1 1 0 0 1 1-1h15a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1m5-6v14l-4-4H8a1 1 0 0 1-1-1v-1h14V8h1a1 1 0 0 1 1 1M8.19 4c-.87 0-1.57.2-2.11.59c-.52.41-.78.98-.77 1.77l.01.03h1.93c.01-.3.1-.53.28-.69a1 1 0 0 1 .66-.23c.31 0 .57.1.75.28c.18.19.26.45.26.75c0 .32-.07.59-.23.82c-.14.23-.35.43-.61.59c-.51.34-.86.64-1.05.91C7.11 9.08 7 9.5 7 10h2c0-.31.04-.56.13-.74s.26-.36.51-.52c.45-.24.82-.53 1.11-.93s.44-.81.44-1.31c0-.76-.27-1.37-.81-1.82C9.85 4.23 9.12 4 8.19 4M7 11v2h2v-2zm6 2h2v-2h-2zm0-9v6h2V4z"></path></svg>
												<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">S.S.S.</span>
											</Link>
										</div>
										{user.user && (
									<>
										<div className="js-nav-dropdown group relative bg-gray-100/50 rounded-lg text-center flex items-center justify-center" onClick={() => setToggle(false)}>
											<Link
												href="/referans"
												className="flex justify-center items-center flex-col text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center gap-4 py-3.5 text-base dark:text-white lg:px-5"
											>
												<BsPersonAdd className="text-2xl"></BsPersonAdd>
												<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Referans Sistemi</span>
											</Link>
										</div>
										<div className="js-nav-dropdown group relative bg-gray-100/50 rounded-lg text-center flex items-center justify-center" onClick={() => setToggle(false)}>
											<button
												onClick={handleLogout}
												className="flex justify-center items-center flex-col text-jacarta-700 font-display hover:text-accent focus:text-accent dark:hover:text-accent dark:focus:text-accent flex items-center gap-4 py-3.5 text-base dark:text-white lg:px-5"
											>
												<BsDoorOpen className="text-2xl"></BsDoorOpen>
												<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Çıkış Yap</span>
											</button>
										</div>
									</>
								)}
									</div>
						</div>
					</div>

					{/* mt-10 w-full lg:hidden */}
				</div>
				{/* End mobile menu and it's other materials */}

				{/* Görev Yerlerim Modal */}
				{showLocationModal && (
					<div className="fixed inset-0 z-50 overflow-y-auto">
						<div className="flex min-h-screen items-center justify-center px-4">
							<div className="fixed inset-0 bg-black/50 backdrop-blur-sm"></div>
							<div className="relative w-full max-w-4xl rounded-lg bg-white p-8 shadow-lg dark:bg-jacarta-800 border dark:border-jacarta-600">
								<div className="mb-6">
									<div className="flex items-center justify-between gap-5">
									<h2 className="text-lg font-bold text-jacarta-700 dark:text-white !mb-1">
										Görev almak istediğiniz yerleri seçiniz
									</h2>
									<button className='bg-gray-100 rounded-full p-2' onClick={() => setShowLocationModal(false)}>
										<svg xmlns="http://www.w3.org/2000/svg" width={24} height={24} viewBox="0 0 24 24"><path fill="currentColor" d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12z"></path></svg>
									</button>
									</div>
									<p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
										Görev yapacağınız alanları il bağımsız olarak birden fazla seçebilirsiniz, en fazla 50 adet seçim yapabilirsiniz.
									</p>
								</div>

								{ showBaroCardAlert && (
									<Link href="/barocard-verify" onClick={() => setShowLocationModal(false)}>
									<div className="bg-indigo-200 hover:bg-indigo-100 border-indigo-300 hover:bg-indigo-200 cursor-pointer text-indigo-900 text-shadow flex p-4 rounded-xl mb-4 items-center gap-5">
										<svg xmlns="http://www.w3.org/2000/svg" width={48} height={48} viewBox="0 0 20 20"><path fill="currentColor" d="m14.878.282l.348 1.071a2.2 2.2 0 0 0 1.399 1.397l1.071.348l.021.006a.423.423 0 0 1 0 .798l-1.071.348a2.2 2.2 0 0 0-1.399 1.397l-.348 1.07a.423.423 0 0 1-.798 0l-.349-1.07a2.2 2.2 0 0 0-.532-.867a2.2 2.2 0 0 0-.866-.536l-1.071-.348a.423.423 0 0 1 0-.798l1.071-.348a2.2 2.2 0 0 0 1.377-1.397l.348-1.07a.423.423 0 0 1 .799 0m4.905 7.931l-.766-.248a1.58 1.58 0 0 1-.998-.999l-.25-.764a.302.302 0 0 0-.57 0l-.248.764a1.58 1.58 0 0 1-.984.999l-.765.248a.303.303 0 0 0 0 .57l.765.249a1.58 1.58 0 0 1 1 1.002l.248.764a.302.302 0 0 0 .57 0l.249-.764a1.58 1.58 0 0 1 .999-.999l.765-.248a.303.303 0 0 0 0-.57zM17.502 12a1.33 1.33 0 0 1-.73-.22A7 7 0 1 1 10.088 3a1.42 1.42 0 0 1 .863-.846l.216-.07a8 8 0 1 0 6.586 9.898a2 2 0 0 1-.251.018m-7.01-3.09A.5.5 0 0 0 9.5 9v4.502l.008.09a.5.5 0 0 0 .992-.09V9zm.307-2.16a.75.75 0 1 0-1.5 0a.75.75 0 0 0 1.5 0"></path></svg>
										<div>
											<div className='font-semibold text-md mb-1'>Önemli bilgilendirme!</div>
											<div>Tevkil görevlerine başvurabilmek için barokart onayınız gerekmektedir. Zor durumda kalmamak için lütfen barokart onayınızı yapınız.</div>
										</div>
									</div>
									</Link>
								)}

								<div className="mb-4">
									<input
										type="text"
										placeholder="Arama yapın"
										className="w-full rounded-lg border border-gray-200 p-3 focus:border-accent focus:ring-accent dark:border-jacarta-600 dark:bg-jacarta-700 dark:text-white"
										value={searchTerm}
										onChange={(e) => setSearchTerm(e.target.value)}
									/>
								</div>

								<div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
									{/* Sol Taraf - Arama Sonuçları */}
									<div className="max-h-96 overflow-y-auto rounded-lg border border-gray-200 p-4 dark:border-jacarta-600">
										{filteredLocations.map((location) => (
											<div
												key={location.id}
												onClick={() => handleLocationSelect(location)}
												className="mb-2 cursor-pointer rounded-lg p-3 hover:bg-gray-100 dark:hover:bg-jacarta-600"
											>
												<div className="font-semibold text-jacarta-700 dark:text-white">
													{location.name}
												</div>
												<div className="text-sm text-gray-500 dark:text-gray-400">
													{location.type} / {location.city}
												</div>
											</div>
										))}
										{filteredLocations.length === 0 && (
											<div className="text-center text-gray-600 dark:text-gray-200">
												{searchTerm ? "Arama sonucu bulunamadı" : "Tüm lokasyonlar seçildi"}
											</div>
										)}
									</div>

									{/* Sağ Taraf - Seçilen Yerler */}
									<div className="max-h-96 overflow-y-auto rounded-lg border border-gray-200 p-4 dark:border-jacarta-600">
										<h3 className="mb-4 font-semibold text-jacarta-700 dark:text-white">
											Seçimleriniz ({selectedLocations.length}/50)
										</h3>
										{selectedLocations.map((location) => (
											<div
												key={location.id}
												className="mb-2 flex items-center justify-between rounded-lg bg-gray-50 p-3 dark:bg-jacarta-700 relative"
											>
												<div>
													<div className="font-semibold text-jacarta-700 dark:text-white">
														{location.name}
													</div>
													<div className="text-sm text-gray-500 dark:text-gray-400">
														{location.type} / {location.city}
													</div>
												</div>
												{(location.rank > 0) && (
													<span className="text-xs text-blue-600 bg-blue-100 rounded-full px-2 py-1 absolute right-10 mr-3">{location.rank}. Sıradasınız</span>
												)}
												<button
													onClick={() => handleLocationRemove(location.id)}
													className="rounded-full bg-red-100 p-1 text-red-500 hover:bg-red-200 dark:bg-red-900/20"
												>
													<svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
													</svg>
												</button>
											</div>
										))}
										{selectedLocations.length === 0 && (
											<div className="text-center text-gray-600 dark:text-gray-200 flex flex-col items-center justify-center">
												<svg xmlns="http://www.w3.org/2000/svg" width="56" height="56" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" strokeLinecap="round" strokeWidth="1.5"><path strokeLinejoin="round" d="m15 18.5l5-5m0 5l-5-5"/><path d="M11 14H3m8 4H3M3 6h10.5M20 6h-2.25M20 10H9.5M3 10h2.25"/></g></svg>
												<span>Görev yeri seçiminiz bulunmamaktadır. <br/> Lütfen sol menüden seçim yapınız.</span>
											</div>
										)}
									</div>
								</div>

								<div className="mt-6 flex justify-end gap-4 sm:flex-row flex-col-reverse">
									<button
										onClick={() => setShowLocationModal(false)}
										className="hidden sm:flex items-center gap-2 rounded-lg bg-gray-100 px-6 py-3 text-gray-700 hover:bg-gray-200 dark:bg-jacarta-700 dark:text-white dark:hover:bg-jacarta-600 justify-center sm:justify-start"
									>
										<svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} viewBox="0 0 24 24"><path fill="currentColor" d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12z"></path></svg>
										Kapat
									</button>
									<button
										onClick={handleSaveLocations}
										className="flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-3 text-white hover:bg-indigo-800 dark:bg-indigo-700 dark:hover:bg-indigo-600 justify-center sm:justify-start"
									>
										<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M2.5 1.75v11.5c0 .138.112.25.25.25h3.17a.75.75 0 0 1 0 1.5H2.75A1.75 1.75 0 0 1 1 13.25V1.75C1 .784 1.784 0 2.75 0h8.5C12.216 0 13 .784 13 1.75v7.736a.75.75 0 0 1-1.5 0V1.75a.25.25 0 0 0-.25-.25h-8.5a.25.25 0 0 0-.25.25m13.274 9.537l-4.557 4.45a.75.75 0 0 1-1.055-.008l-1.943-1.95a.75.75 0 0 1 1.062-1.058l1.419 1.425l4.026-3.932a.75.75 0 1 1 1.048 1.074M4.75 4h4.5a.75.75 0 0 1 0 1.5h-4.5a.75.75 0 0 1 0-1.5M4 7.75A.75.75 0 0 1 4.75 7h2a.75.75 0 0 1 0 1.5h-2A.75.75 0 0 1 4 7.75"/></svg>
										Seçimleri Kaydet
									</button>
								</div>
							</div>
						</div>
					</div>
				)}

				<div className="fixed lg:hidden bottom-0 left-0 w-full bg-white dark:bg-jacarta-900 z-20 border-t dark:border-t-jacarta-600">
					<div className="flex flex-row py-4">

						{isLogged ? (
							<>
								<div className="basis-1/4">
									<Link href="/gorevler/liste">
										<div className="flex flex-col items-center">
											<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
												<path d="M11 4H21V6H11V4ZM11 8H17V10H11V8ZM11 14H21V16H11V14ZM11 18H17V20H11V18ZM3 4H9V10H3V4ZM5 6V8H7V6H5ZM3 14H9V20H3V14ZM5 16V18H7V16H5Z"></path>
											</svg>
											<span className="text-xs text-black dark:text-white/90">Aktif Görevler</span>
										</div>
									</Link>
								</div>
								<div className="basis-1/4">
									<Link href="/gorevler/olustur">
										<div className="flex flex-col items-center">
											<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
												<path d="M11 11V5H13V11H19V13H13V19H11V13H5V11H11Z"></path>
											</svg>
											<span className="text-xs text-black dark:text-white/90">Görev Oluştur</span>
										</div>
									</Link>
								</div>
								<div className="basis-1/4">
									<NotificationMobile notifications={notifications} setNotifications={setNotifications} setShowLocationModal={setShowLocationModal} />
								</div>
								<div className="basis-1/4">
									<div className="flex flex-col items-center" onClick={() => setToggle(true)}>
										<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
											<path d="M3 4H21V6H3V4ZM9 11H21V13H9V11ZM3 18H21V20H3V18Z"></path>
										</svg>
										<span className="text-xs text-black dark:text-white/90">Menü</span>
									</div>
								</div>
								
							</>
						) : (
							<>
								<div className="basis-1/4">
									<Link href="/">
										<div className="flex flex-col items-center">
											<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
												<path d="M19 21H5C4.44772 21 4 20.5523 4 20V11L1 11L11.3273 1.6115C11.7087 1.26475 12.2913 1.26475 12.6727 1.6115L23 11L20 11V20C20 20.5523 19.5523 21 19 21ZM13 19H18V9.15745L12 3.7029L6 9.15745V19H11V13H13V19Z"></path>
											</svg>
											<span className="text-xs text-black dark:text-white/90">Anasayfa</span>
										</div>
									</Link>
								</div>
								<div className="basis-1/4">
									<Link href="/login">
										<div className="flex flex-col items-center">
											<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
												<path d="M14 14.252V16.3414C13.3744 16.1203 12.7013 16 12 16C8.68629 16 6 18.6863 6 22H4C4 17.5817 7.58172 14 12 14C12.6906 14 13.3608 14.0875 14 14.252ZM12 13C8.685 13 6 10.315 6 7C6 3.685 8.685 1 12 1C15.315 1 18 3.685 18 7C18 10.315 15.315 13 12 13ZM12 11C14.21 11 16 9.21 16 7C16 4.79 14.21 3 12 3C9.79 3 8 4.79 8 7C8 9.21 9.79 11 12 11ZM18.5858 17L16.7574 15.1716L18.1716 13.7574L22.4142 18L18.1716 22.2426L16.7574 20.8284L18.5858 19H15V17H18.5858Z"></path>
											</svg>
											<span className="text-xs text-black dark:text-white/90">Giriş / Kayıt</span>
										</div>
									</Link>
								</div>
								<div className="basis-1/4">
									<Link href="/gorev-olustur">
										<div className="flex flex-col items-center">
											<svg className="w-6 h-6" xmlns="http://www.w3.org/2000/svg" width={12} height={12} viewBox="0 0 24 24"><g fill="none" stroke="currentColor" strokeWidth={2}><path d="M12 4C8.229 4 6.343 4 5.172 5.172S4 8.229 4 12v6c0 .943 0 1.414.293 1.707S5.057 20 6 20h6c3.771 0 5.657 0 6.828-1.172S20 15.771 20 12"></path><path strokeLinecap="round" strokeLinejoin="round" d="M9 10h6m-6 4h3m7-6V2m-3 3h6"></path></g></svg>
											<span className="text-xs text-black dark:text-white/90">Tevkil Oluştur</span>
										</div>
									</Link>
								</div>
								<div className="basis-1/4">
									<div className="flex flex-col items-center" onClick={() => setToggle(true)}>
										<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
											<path d="M3 4H21V6H3V4ZM9 11H21V13H9V11ZM3 18H21V20H3V18Z"></path>
										</svg>
										<span className="text-xs text-black dark:text-white/90">Menü</span>
									</div>
								</div>
							</>
						)}
					</div>
				</div>
			</>
		) : (isLogged && (
			<>
				{/* main dropdown menu sart*/}
				<header
					className="js-page-header absolute sm:fixed top-0 z-20 w-full backdrop-blur transition-colors dark:bg-none">
					<div className="flex items-center py-6 ml-auto mr-auto h-full max-w-[91rem] px-4 ">
						<Link className="shrink-0" href="/">
							<div className="dark:hidden">
								<Image
									src={Logo}
									style={{height: 'auto', width: '170px'}}
									alt="TevkilApp | Avukatlar arası görev paylaşım platformu"
								/>
							</div>
							<div className="hidden dark:block">
								<Image
									src={WhiteLogo}
									style={{height: 'auto', width: '170px'}}
									alt="TevkilApp | Avukatlar arası görev paylaşım platformu"
								/>
							</div>
						</Link>
						{/* End  logo */}


						<div
							className="js-mobile-menu dark:bg-jacarta-800 invisible fixed inset-0 z-10 ml-auto items-center bg-white opacity-0 lg:visible lg:relative lg:inset-auto lg:flex lg:bg-transparent lg:opacity-100 dark:lg:bg-transparent">

							<div className="ml-8 hidden items-center lg:flex xl:ml-12">
								<div className="js-nav-dropdown group-dropdown relative">
									<button
										className="dropdown-toggle border-jacarta-100 hover:bg-accent focus:bg-accent group dark:hover:bg-accent ml-2 flex h-10 w-10 items-center justify-center rounded-full border bg-white transition-colors hover:border-transparent focus:border-transparent dark:border-transparent dark:bg-white/[.15]">
										<svg
											xmlns="http://www.w3.org/2000/svg"
											viewBox="0 0 24 24"
											width={24}
											height={24}
											className="fill-jacarta-700 h-4 w-4 transition-colors group-hover:fill-white group-focus:fill-white dark:fill-white"
										>
											<path fill="none" d="M0 0h24v24H0z"/>
											<path d="M11 14.062V20h2v-5.938c3.946.492 7 3.858 7 7.938H4a8.001 8.001 0 0 1 7-7.938zM12 13c-3.315 0-6-2.685-6-6s2.685-6 6-6 6 2.685 6 6-2.685 6-6 6z"/>
										</svg>
									</button>
									<div
										className="dropdown-menu dark:bg-jacarta-800 group-dropdown-hover:opacity-100 group-dropdown-hover:visible !-right-4 !top-[85%] !left-auto z-10 min-w-[16rem] whitespace-nowrap rounded-xl bg-white transition-all will-change-transform before:absolute before:-top-3 before:h-3 before:w-full lg:absolute lg:grid lg:!translate-y-4 lg:py-4 lg:px-2 lg:shadow-2xl hidden lg:invisible lg:opacity-0">

										{isLogged ? (<UserAuthDropdown mobileUserDropdown={mobileUserDropdown} setMobileUserDropdown={setMobileUserDropdown} user={user.user}/>) : (<UserNotLoggedIn/>)}

									</div>
								</div>
								<DarkMode/>
							</div>
							{/* End header right content (metamask and other) for dropdown */}
						</div>
						{/* header menu conent end for dropdown */}

						{/*mobile taraflı user dropdown kısmı*/}
						<div className="ml-auto flex relative lg:hidden">
							<div className="">
								<button
									onClick={() => setMobileUserDropdown(!mobileUserDropdown)}
									
									className={`absolute !right-24 border-jacarta-100 ${mobileUserDropdown ? 'bg-accent dark:bg-accent border-transparent' : 'dark:bg-white/[.15]  bg-white '} group ml-2 flex h-10 w-10 items-center justify-center rounded-full border  transition-colors  dark:border-transparent `}>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										viewBox="0 0 24 24"
										width={24}
										height={24}
										className={` h-4 w-4 transition-colors  ${mobileUserDropdown ? 'fill-white  ' : 'fill-jacarta-700 dark:fill-white'}`}
									>
										<path fill="none" d="M0 0h24v24H0z"/>
										<path d="M11 14.062V20h2v-5.938c3.946.492 7 3.858 7 7.938H4a8.001 8.001 0 0 1 7-7.938zM12 13c-3.315 0-6-2.685-6-6s2.685-6 6-6 6 2.685 6 6-2.685 6-6 6z"/>
									</svg>
								</button>
								<div
									style={{display: mobileUserDropdown ? 'block' : 'none'}}
									className="dark:bg-jacarta-800 mt-5 pt-4 pb-4 !right-14 absolute !top-[85%] !left-auto z-10 min-w-[16rem] whitespace-nowrap rounded-xl bg-white transition-all will-change-transform before:absolute before:-top-3 before:h-3 before:w-full lg:absolute lg:grid lg:!translate-y-4 lg:py-4 lg:px-2 lg:shadow-2xl">
									{isLogged ? (<UserAuthDropdown mobileUserDropdown={mobileUserDropdown} setMobileUserDropdown={setMobileUserDropdown} user={user.user}/>) : (<UserNotLoggedIn/>)}

								</div>
							</div>
							<DarkMode/>
						</div>
						{/* End header right content  for mobile */}
					</div>
					{/* End flex item */}
				</header>
				{/* main dropdown menu end */}

				{/* start mobile menu and it's other materials  */}
				<div className={`lg:hidden js-mobile-menu dark:bg-jacarta-800 invisible fixed inset-0 z-20 ml-auto items-center bg-white opacity-0 lg:visible lg:relative lg:inset-auto lg:bg-transparent lg:opacity-100 dark:lg:bg-transparent ${toggle ? 'nav-menu--is-open' : 'hidden'}`}>
					<div className="t-0 dark:bg-jacarta-800 fixed left-0 z-10 flex w-full items-center justify-between bg-white p-6 lg:hidden">
						<div className="dark:hidden">
							<Image
								src={Logo}
								height={28}
								width={130}
								alt="TevkilApp - İşlerinizi Kolaylaştırın, Sonuçları Hızlandırın, Hukuki Yükümlülükleri TevkilApp İle Sorunsuz Yönetin!"
								className="max-h-7 h-auto object-cover" 
							/>
						</div>

						<div className="hidden dark:block">
							<Image
								src={WhiteLogo}
								height={28}
								width={130}
								alt="TevkilApp - İşlerinizi Kolaylaştırın, Sonuçları Hızlandırın, Hukuki Yükümlülükleri TevkilApp İle Sorunsuz Yönetin!"
							/>
						</div>

						<button
							className="js-mobile-close border-jacarta-100 hover:bg-accent focus:bg-accent group dark:hover:bg-accent ml-2 flex h-10 w-10 items-center justify-center rounded-full border bg-white transition-colors hover:border-transparent focus:border-transparent dark:border-transparent dark:bg-white/[.15]"
							onClick={() => setToggle(false)}
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								width={24}
								height={24}
								className="fill-jacarta-700 h-4 w-4 transition-colors group-hover:fill-white group-focus:fill-white dark:fill-white"
							>
								<path fill="none" d="M0 0h24v24H0z"/>
								<path d="M12 10.586l4.95-4.95 1.414 1.414-4.95 4.95 4.95 4.95-1.414 1.414-4.95-4.95-4.95 4.95-1.414-1.414 4.95-4.95-4.95-4.95L7.05 5.636z"/>
							</svg>
						</button>
					</div>

					{/* End navbar mobile menu  */}

					<div className="w-full lg:hidden">

						<hr className="dark:bg-jacarta-600 bg-jacarta-100 my-5 h-px border-0"/>
						<div className="flex items-center justify-center space-x-5">
							<a className="group">
								<svg
									aria-hidden="true"
									focusable="false"
									data-prefix="fab"
									data-icon="facebook"
									className="group-hover:fill-accent fill-jacarta-300 h-5 w-5 dark:group-hover:fill-white"
									role="img"
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 512 512"
								>
									<path d="M504 256C504 119 393 8 256 8S8 119 8 256c0 123.78 90.69 226.38 209.25 245V327.69h-63V256h63v-54.64c0-62.15 37-96.48 93.67-96.48 27.14 0 55.52 4.84 55.52 4.84v61h-31.28c-30.8 0-40.41 19.12-40.41 38.73V256h68.78l-11 71.69h-57.78V501C413.31 482.38 504 379.78 504 256z"/>
								</svg>
							</a>
							<a className="group">
								<svg
									aria-hidden="true"
									focusable="false"
									data-prefix="fab"
									data-icon="twitter"
									className="group-hover:fill-accent fill-jacarta-300 h-5 w-5 dark:group-hover:fill-white"
									role="img"
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 512 512"
								>
									<path d="M459.37 151.716c.325 4.548.325 9.097.325 13.645 0 138.72-105.583 298.558-298.558 298.558-59.452 0-114.68-17.219-161.137-47.106 8.447.974 16.568 1.299 25.34 1.299 49.055 0 94.213-16.568 130.274-44.832-46.132-.975-84.792-31.188-98.112-72.772 6.498.974 12.995 1.624 19.818 1.624 9.421 0 18.843-1.3 27.614-3.573-48.081-9.747-84.143-51.98-84.143-102.985v-1.299c13.969 7.797 30.214 12.67 47.431 13.319-28.264-18.843-46.781-51.005-46.781-87.391 0-19.492 5.197-37.36 14.294-52.954 51.655 63.675 129.3 105.258 216.365 109.807-1.624-7.797-2.599-15.918-2.599-24.04 0-57.828 46.782-104.934 104.934-104.934 30.213 0 57.502 12.67 76.67 33.137 23.715-4.548 46.456-13.32 66.599-25.34-7.798 24.366-24.366 44.833-46.132 57.827 21.117-2.273 41.584-8.122 60.426-16.243-14.292 20.791-32.161 39.308-52.628 54.253z"/>
								</svg>
							</a>
							<a className="group">
								<svg
									aria-hidden="true"
									focusable="false"
									data-prefix="fab"
									data-icon="discord"
									className="group-hover:fill-accent fill-jacarta-300 h-5 w-5 dark:group-hover:fill-white"
									role="img"
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 640 512"
								>
									<path d="M524.531,69.836a1.5,1.5,0,0,0-.764-.7A485.065,485.065,0,0,0,404.081,32.03a1.816,1.816,0,0,0-1.923.91,337.461,337.461,0,0,0-14.9,30.6,447.848,447.848,0,0,0-134.426,0,309.541,309.541,0,0,0-15.135-30.6,1.89,1.89,0,0,0-1.924-.91A483.689,483.689,0,0,0,116.085,69.137a1.712,1.712,0,0,0-.788.676C39.068,183.651,18.186,294.69,28.43,404.354a2.016,2.016,0,0,0,.765,1.375A487.666,487.666,0,0,0,176.02,479.918a1.9,1.9,0,0,0,2.063-.676A348.2,348.2,0,0,0,208.12,430.4a1.86,1.86,0,0,0-1.019-2.588,321.173,321.173,0,0,1-45.868-21.853,1.885,1.885,0,0,1-.185-3.126c3.082-2.309,6.166-4.711,9.109-7.137a1.819,1.819,0,0,1,1.9-.256c96.229,43.917,200.41,43.917,295.5,0a1.812,1.812,0,0,1,1.924.233c2.944,2.426,6.027,4.851,9.132,7.16a1.884,1.884,0,0,1-.162,3.126,301.407,301.407,0,0,1-45.89,21.83,1.875,1.875,0,0,0-1,2.611,391.055,391.055,0,0,0,30.014,48.815,1.864,1.864,0,0,0,2.063.7A486.048,486.048,0,0,0,610.7,405.729a1.882,1.882,0,0,0,.765-1.352C623.729,277.594,590.933,167.465,524.531,69.836ZM222.491,337.58c-28.972,0-52.844-26.587-52.844-59.239S193.056,219.1,222.491,219.1c29.665,0,53.306,26.82,52.843,59.239C275.334,310.993,251.924,337.58,222.491,337.58Zm195.38,0c-28.971,0-52.843-26.587-52.843-59.239S388.437,219.1,417.871,219.1c29.667,0,53.307,26.82,52.844,59.239C470.715,310.993,447.538,337.58,417.871,337.58Z"/>
								</svg>
							</a>
							<a className="group">
								<svg
									aria-hidden="true"
									focusable="false"
									data-prefix="fab"
									data-icon="instagram"
									className="group-hover:fill-accent fill-jacarta-300 h-5 w-5 dark:group-hover:fill-white"
									role="img"
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 448 512"
								>
									<path d="M224.1 141c-63.6 0-114.9 51.3-114.9 114.9s51.3 114.9 114.9 114.9S339 319.5 339 255.9 287.7 141 224.1 141zm0 189.6c-41.1 0-74.7-33.5-74.7-74.7s33.5-74.7 74.7-74.7 74.7 33.5 74.7 74.7-33.6 74.7-74.7 74.7zm146.4-194.3c0 14.9-12 26.8-26.8 26.8-14.9 0-26.8-12-26.8-26.8s12-26.8 26.8-26.8 26.8 12 26.8 26.8zm76.1 27.2c-1.7-35.9-9.9-67.7-36.2-93.9-26.2-26.2-58-34.4-93.9-36.2-37-2.1-147.9-2.1-184.9 0-35.8 1.7-67.6 9.9-93.9 36.1s-34.4 58-36.2 93.9c-2.1 37-2.1 147.9 0 184.9 1.7 35.9 9.9 67.7 36.2 93.9s58 34.4 93.9 36.2c37 2.1 147.9 2.1 184.9 0 35.9-1.7 67.7-9.9 93.9-36.2 26.2-26.2 34.4-58 36.2-93.9 2.1-37 2.1-147.8 0-184.8zM398.8 388c-7.8 19.6-22.9 34.7-42.6 42.6-29.5 11.7-99.5 9-132.1 9s-102.7 2.6-132.1-9c-19.6-7.8-34.7-22.9-42.6-42.6-11.7-29.5-9-99.5-9-132.1s-2.6-102.7 9-132.1c7.8-19.6 22.9-34.7 42.6-42.6 29.5-11.7 99.5-9 132.1-9s102.7-2.6 132.1 9c19.6 7.8 34.7 22.9 42.6 42.6 11.7 29.5 9 99.5 9 132.1s2.7 102.7-9 132.1z"/>
								</svg>
							</a>
							<a className="group">
								<svg
									aria-hidden="true"
									focusable="false"
									data-prefix="fab"
									data-icon="tiktok"
									className="group-hover:fill-accent fill-jacarta-300 h-5 w-5 dark:group-hover:fill-white"
									role="img"
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 448 512"
								>
									<path d="M448,209.91a210.06,210.06,0,0,1-122.77-39.25V349.38A162.55,162.55,0,1,1,185,188.31V278.2a74.62,74.62,0,1,0,52.23,71.18V0l88,0a121.18,121.18,0,0,0,1.86,22.17h0A122.18,122.18,0,0,0,381,102.39a121.43,121.43,0,0,0,67,20.14Z"/>
								</svg>
							</a>
						</div>
					</div>
					{/* mt-10 w-full lg:hidden */}
				</div>
				{/* End mobile menu and it's other materials */}

				{/*
				<div className="fixed bottom-0 left-0 w-full bg-red-500">
					asd
				</div>
				*/}
			</>
		))));
}
