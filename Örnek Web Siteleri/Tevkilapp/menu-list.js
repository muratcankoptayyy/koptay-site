import Link from 'next/link';
import {BsCreditCard2FrontFill, BsFillEnvelopeAtFill, BsKeyFill, BsPhoneFill, BsPersonSquare, BsFillTrash3Fill} from 'react-icons/bs';
import React, {useEffect} from 'react';

const MenuList = () => {
	const activeTab = () => {
		const path = window.location.pathname;
		const menuList = document.querySelectorAll('.menu-list a');
		for (let i = 0; i < menuList.length; i++) {
			if (menuList[i].getAttribute('href') === path) {
				menuList[i].classList.add('!bg-indigo-100');
				menuList[i].classList.add('!border-indigo-300');
				menuList[i].classList.add('!text-indigo-900');
				menuList[i].classList.add('dark:!bg-indigo-700');
				menuList[i].classList.add('dark:!text-indigo-100');
				menuList[i].classList.add('dark:!border-indigo-500');
			}
		}
	};

	useEffect(() => {
		activeTab();
	}, []);

	return (
		<div className="flex gap-2 flex-col sm:flex-row justify-center menu-list">
			{/*<Link*/}
			{/*	href="/settings"*/}
			{/*	className="font-display dark:text-white/70 dark:hover:text-white text-gray-600 hover:text-jacarta-700 transition-colors bg-gray-50 dark:bg-jacarta-700 p-2 px-6 rounded-full border dark:border-jacarta-600 flex flex-row items-center gap-3">*/}
			{/*	<BsClipboardDataFill></BsClipboardDataFill>*/}
			{/*	Özet Ekranı*/}
			{/*</Link>*/}
			<Link
				href="/ayarlar/parola-degistir"
				className="font-display dark:text-white/70 dark:hover:text-white text-gray-600 hover:text-jacarta-700 transition-colors bg-gray-50 dark:bg-jacarta-700 p-2 px-6 rounded-full border dark:border-jacarta-600 flex flex-row items-center gap-3">
				<BsKeyFill></BsKeyFill>
				Şifre Değiştir
			</Link>
			{/*<Link*/}
			{/*	href="/ayarlar/email-degistir"*/}
			{/*	className="font-display dark:text-white/70 dark:hover:text-white text-gray-600 hover:text-jacarta-700 transition-colors bg-gray-50 dark:bg-jacarta-700 p-2 px-6 rounded-full border dark:border-jacarta-600 flex flex-row items-center gap-3">*/}
			{/*	<BsFillEnvelopeAtFill></BsFillEnvelopeAtFill>*/}
			{/*	E-Mail Değiştir*/}
			{/*</Link>*/}
			{/*<Link*/}
			{/*	href="/ayarlar/telefon-degistir"*/}
			{/*	className="font-display dark:text-white/70 dark:hover:text-white text-gray-600 hover:text-jacarta-700 transition-colors bg-gray-50 dark:bg-jacarta-700 p-2 px-6 rounded-full border dark:border-jacarta-600 flex flex-row items-center gap-3">*/}
			{/*	<BsPhoneFill></BsPhoneFill>*/}
			{/*	Telefon Değiştir*/}
			{/*</Link>*/}
			<Link
				href="/ayarlar/bakiye-hareketleri"
				className="font-display dark:text-white/70 dark:hover:text-white text-gray-600 hover:text-jacarta-700 transition-colors bg-gray-50 dark:bg-jacarta-700 p-2 px-6 rounded-full border dark:border-jacarta-600 flex flex-row items-center gap-3">
				<BsCreditCard2FrontFill></BsCreditCard2FrontFill>
				Bakiye Hareketlerim
			</Link>
			<Link
				href="/ayarlar/avatar-degistir"
				className="font-display dark:text-white/70 dark:hover:text-white text-gray-600 hover:text-jacarta-700 transition-colors bg-gray-50 dark:bg-jacarta-700 p-2 px-6 rounded-full border dark:border-jacarta-600 flex flex-row items-center gap-3">
				<BsPersonSquare></BsPersonSquare>
				Profil Fotoğrafı
			</Link>
			{/* <Link
				href="/ayarlar/hesabi-sil"
				className="font-display dark:text-white/70 dark:hover:text-white text-gray-600 hover:text-jacarta-700 transition-colors bg-gray-50 dark:bg-jacarta-700 p-2 px-6 rounded-full border dark:border-jacarta-600 flex flex-row items-center gap-3">
				<BsFillTrash3Fill></BsFillTrash3Fill>
				Hesabı Sil
			</Link> */}
		</div>
	);
};

export default MenuList;