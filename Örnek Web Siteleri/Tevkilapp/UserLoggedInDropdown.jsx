import Image from 'next/image';
import Link from 'next/link';
import {BsCardChecklist, BsDoorOpen, BsLifePreserver, BsPersonAdd, BsPersonGear, BsPlusLg, BsReceipt, BsStar, BsGeoAlt} from 'react-icons/bs';
import {HiQueueList} from 'react-icons/hi2';
import {logout} from '../../../redux/slices/userSlice';
import Cookies from 'js-cookie';
import {useDispatch} from 'react-redux';
import {useRouter} from 'next/router';
import React, {useState, useEffect} from 'react';
import Swal from 'sweetalert2';

export const UserLoggedInDropdown = ({user, setMobileUserDropdown, mobileUserDropdown, setShowLocationModal}) => {
	const dispatch = useDispatch();
	const route = useRouter();
	const [userState, setUserState] = useState(null);

	useEffect(() => {
		const userData = localStorage.getItem('user');
		if (userData) {
			setUserState(JSON.parse(userData));
		}
	}, []);

	const handleCloseDropdown = () => {
		setMobileUserDropdown(false);
	};

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
			localStorage.removeItem('user');
			localStorage.removeItem('userToken');
			window.location.reload();
			
			await Swal.fire({
				title: 'Çıkış Yapıldı!',
				text: 'Başarıyla çıkış yaptınız.',
				icon: 'success',
				timer: 1500,
				showConfirmButton: false
			});
		}
	};

	return (
		user && (
			<div className="js-nav-dropdown group-dropdown relative">
				<button className="dropdown-toggle flex justify-center items-center gap-2 px-8 py-3 bg-white/30 hover:shadow-lg hover:shadow-gray-100/30 rounded-full text-gray-800 font-display hover:bg-white hover:text-blackb dark:hover:text-accent flex items-center justify-between py-3.5 text-base dark:text-white lg:px-5">
					{/* <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 256 256"><path fill="currentColor" d="M230.93 220a8 8 0 0 1-6.93 4H32a8 8 0 0 1-6.92-12c15.23-26.33 38.7-45.21 66.09-54.16a72 72 0 1 1 73.66 0c27.39 8.95 50.86 27.83 66.09 54.16a8 8 0 0 1 .01 8"/></svg> */}
					<Image src={`https://cdn.tevkilapp.com/${user.avatar}`}
								style={{height: 'auto', width: 'auto'}}
								height={18}
								alt="avatar"
								width={18}
								quality={90}
								className="max-h-[27px] my-[-10px] rounded-full"/>
					<span>{user.full_name.length > 18 ? user.full_name.substring(0, 10) + '...' : user.full_name}</span>
				</button>
				<div className="dropdown-menu dark:bg-jacarta-800 group-dropdown-hover:opacity-100 group-dropdown-hover:visible !-right-4 !top-[85%] !left-auto z-10 min-w-[16rem] whitespace-nowrap rounded-xl bg-white transition-all will-change-transform before:absolute before:-top-3 before:h-3 before:w-full lg:absolute lg:grid lg:!translate-y-4 lg:py-4 lg:px-2 lg:shadow-2xl hidden lg:invisible lg:opacity-0">					
				<div onClick={handleCloseDropdown}>
				{userState?.mail_verify_at === null && (
						<Link
						href="/email-verify"
						className="mb-1 bg-red-100/40 text-red-600 hover:text-red-900 hover:bg-red-200 flex items-center space-x-2 rounded-xl px-5 py-2 transition-colors"
						>
							<svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} viewBox="0 0 24 24"><path fill="currentColor" d="M12 15c.81 0 1.5-.3 2.11-.89c.59-.61.89-1.3.89-2.11s-.3-1.5-.89-2.11C13.5 9.3 12.81 9 12 9s-1.5.3-2.11.89C9.3 10.5 9 11.19 9 12s.3 1.5.89 2.11c.61.59 1.3.89 2.11.89m0-13c2.75 0 5.1 1 7.05 2.95S22 9.25 22 12v1.45c0 1-.35 1.85-1 2.55c-.7.67-1.5 1-2.5 1c-1.2 0-2.19-.5-2.94-1.5c-1 1-2.18 1.5-3.56 1.5c-1.37 0-2.55-.5-3.54-1.46C7.5 14.55 7 13.38 7 12c0-1.37.5-2.55 1.46-3.54C9.45 7.5 10.63 7 12 7c1.38 0 2.55.5 3.54 1.46C16.5 9.45 17 10.63 17 12v1.45c0 .41.16.77.46 1.08s.65.47 1.04.47c.42 0 .77-.16 1.07-.47s.43-.67.43-1.08V12c0-2.19-.77-4.07-2.35-5.65S14.19 4 12 4s-4.07.77-5.65 2.35S4 9.81 4 12s.77 4.07 2.35 5.65S9.81 20 12 20h5v2h-5c-2.75 0-5.1-1-7.05-2.95S2 14.75 2 12s1-5.1 2.95-7.05S9.25 2 12 2"></path></svg>
							<span className="font-display text-red-600 mt-1 text-sm">E-Mail Doğrula</span>
						</Link>
					)}

					{userState?.user_verify_at === null && (
						<Link
						href="/barocard-verify"
						className="mb-1 bg-indigo-100/40 text-indigo-700 hover:text-indigo-900 hover:bg-indigo-200 flex items-center space-x-2 rounded-xl px-5 py-2 transition-colors"
						>
							<svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} viewBox="0 0 24 24"><path fill="currentColor" d="M3 6h18v12H3zM2 4a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h20a1 1 0 0 0 1-1V5a1 1 0 0 0-1-1zm11 4h6v2h-6zm5 4h-5v2h5zm-7.5-2a2.5 2.5 0 1 1-5 0a2.5 2.5 0 0 1 5 0M8 13.5A3.5 3.5 0 0 0 4.5 17h7A3.5 3.5 0 0 0 8 13.5"></path></svg>
							<span className="font-display text-indigo-700 mt-1 text-sm">Baro Kart Doğrula</span>
						</Link>
					)}
					<Link
						href="/premium"
						className="dark:hover:bg-jacarta-600 hover:text-accent focus:text-accent hover:bg-jacarta-50 flex items-center space-x-2 rounded-xl px-5 py-2 transition-colors"
					>
						<BsStar></BsStar>
						<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Premium Üyelik</span>
					</Link>
					<hr className="mt-2 mb-2 -mx-2 dark:border-jacarta-600"/>
					<Link
						href="/gorevler/olustur"
						className="dark:hover:bg-jacarta-600 hover:text-accent focus:text-accent hover:bg-jacarta-50 flex items-center space-x-2 rounded-xl px-5 py-2 transition-colors"
					>
						<BsPlusLg></BsPlusLg>
						<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Tevkil Oluştur</span>
					</Link>
					<Link
						href="/gorevler/gorevlerim"
						className="dark:hover:bg-jacarta-600 hover:text-accent focus:text-accent hover:bg-jacarta-50 flex items-center space-x-2 rounded-xl px-5 py-2 transition-colors"
					>
						<BsReceipt></BsReceipt>
						<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Oluşturduğum Görevler</span>
					</Link>
					<Link
						href="/gorevler/katildiklarim"
						className="dark:hover:bg-jacarta-600 hover:text-accent focus:text-accent hover:bg-jacarta-50 flex items-center space-x-2 rounded-xl px-5 py-2 transition-colors"
					>
						<BsCardChecklist></BsCardChecklist>
						<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Başvurduğum Görevler</span>
					</Link>
					{/* <Link
						href="/sira"
						className="dark:hover:bg-jacarta-600 hover:text-accent focus:text-accent hover:bg-jacarta-50 flex items-center space-x-2 rounded-xl px-5 py-2 transition-colors"
					>
						<HiQueueList></HiQueueList>
						<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Görev Sıralarımxxx</span>
					</Link> */}
					<button
						onClick={() => {
							setShowLocationModal(true);
							setMobileUserDropdown(false);
						}}
						className="dark:hover:bg-jacarta-600 hover:text-accent focus:text-accent hover:bg-jacarta-50 flex items-center space-x-2 rounded-xl px-5 py-2 transition-colors w-full"
					>
						<BsGeoAlt></BsGeoAlt>
						<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Görev Yerlerim</span>
					</button>

					<hr className="mt-2 mb-2 -mx-2 dark:border-jacarta-600"/>

					<Link
						href="/ayarlar/avatar-degistir"
						className="dark:hover:bg-jacarta-600 hover:text-accent focus:text-accent hover:bg-jacarta-50 flex items-center space-x-2 rounded-xl px-5 py-2 transition-colors"
					>
						<BsPersonGear></BsPersonGear>
						<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Ayarlarım</span>
					</Link>
					<Link
						href="/destek/liste"
						className="dark:hover:bg-jacarta-600 hover:text-accent focus:text-accent hover:bg-jacarta-50 flex items-center space-x-2 rounded-xl px-5 py-2 transition-colors"
					>
						<BsLifePreserver></BsLifePreserver>
						<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Destek Sistemi</span>
					</Link>
					<Link
						href="/referans"
						className="dark:hover:bg-jacarta-600 hover:text-accent focus:text-accent hover:bg-jacarta-50 flex items-center space-x-2 rounded-xl px-5 py-2 transition-colors"
					>
						<BsPersonAdd></BsPersonAdd>
						<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Referans Sistemi</span>
					</Link>
					<button
						onClick={handleLogout}
						className="dark:hover:bg-jacarta-600 hover:text-accent focus:text-accent hover:bg-jacarta-50 flex items-center space-x-2 rounded-xl px-5 py-2 transition-colors w-full"
					>
						<BsDoorOpen></BsDoorOpen>
						<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Çıkış Yap</span>
					</button>
				</div>
			</div>
		</div>
		)
	);
};