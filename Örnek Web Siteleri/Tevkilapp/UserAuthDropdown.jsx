import Image from 'next/image';
import Link from 'next/link';
import {BsCardChecklist, BsDoorOpen, BsLifePreserver, BsPersonAdd, BsPersonGear, BsPlusLg, BsReceipt, BsStar} from 'react-icons/bs';
import {HiQueueList} from 'react-icons/hi2';
import {logout} from '../../../redux/slices/userSlice';
import Cookies from 'js-cookie';
import {useDispatch} from 'react-redux';
import {useRouter} from 'next/router';
import React from 'react';

export const UserAuthDropdown = ({user, setMobileUserDropdown, mobileUserDropdown}) => {
	const dispatch = useDispatch();
	const route = useRouter();

	const handleCloseDropdown = () => {
		setMobileUserDropdown(false);
	};

	const handleLogout = () => {
		dispatch(logout());
		Cookies.remove('userToken');
		Cookies.remove('user');
		route.push('/uyelik/giris');
	};

	return (
		user && (
			<div onClick={handleCloseDropdown}>
				<div className="flex flex-row bg-gray-100 m-3 p-2 rounded-lg align-middle gap-3 mt-0 items-center dark:bg-jacarta-900">
					<Image src={`https://cdn.tevkilapp.com/${user.avatar}`}
							 style={{height: 'auto', width: 'auto'}}
							 height={50}
							 alt="avatar"
							 width={50}
							 quality={90}
							 className="rounded-lg max-h-[60px]"/>
					<div>
						<div className="font-display font-semibold text-sm text-three-dot-mobile sm:text-three-dot"
							  style={{height: '18px'}}>
							{user.full_name.length > 18 ? user.full_name.substring(0, 15) + '...' : user.full_name}
						</div>

						<span className="text-sm">Avukat</span>
					</div>
				</div>

				<button
					onClick={handleLogout}
					className="dark:hover:bg-jacarta-600 hover:text-accent focus:text-accent hover:bg-jacarta-50 flex items-center space-x-2 rounded-xl px-5 py-2 transition-colors w-full"
				>
					<BsDoorOpen></BsDoorOpen>
					<span className="font-display text-jacarta-700 mt-1 text-sm dark:text-white">Çıkış Yap</span>
				</button>
			</div>
		)
	);
};