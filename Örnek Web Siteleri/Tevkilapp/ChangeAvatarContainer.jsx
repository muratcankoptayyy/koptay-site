import React, {useEffect, useState} from 'react';
import request from '../../../utils/request';
import Swal from 'sweetalert2';
import {useSelector} from 'react-redux';
import Image from 'next/image';
import LoaderComponent from '../../../components/LoaderComponent';

const ChangeAvatarContainer = () => {
	const [profilePhoto, setProfilePhoto] = useState();
	const [statusText, setStatusText] = useState('');
	const [preview, setPreview] = useState();
	const [loading, setLoading] = useState(false);

	const user = useSelector(state => state.user);

	const handleUpdateProfile = async (e) => {
		const formData = new FormData();
		e.preventDefault();
		setLoading(true);
		formData.append('file', e.target.files[0]);

		const response = await request('/user/avatar/upload', 'POST', formData, true, true);
		if (response.success) {
			await Swal.fire({
				icon: 'success',
				title: 'Başarılı',
				text: 'Profil fotoğrafınızı güncelleme istediğiniz iletildi!',
				showConfirmButton: false,
				timer: 1500,
			});
			setStatusText({
				message: 'Avatar değiştirme talebiniz bulunmaktadır.',
				id: response.data.id,

			});
		}
		else {
			await Swal.fire({
				icon: 'error',
				title: 'Hata',
				text: 'Profil fotoğrafınızı güncelleme istedğiniz iletilemedi!',
				showConfirmButton: false,
				timer: 1500,
			});
		}
		setLoading(false);
	};

	const handleProfilePhoto = async (e) => {
		const file = e.target.files[0];
		if (file && !file.type.includes('image')) {
			await Swal.fire({
				icon: 'error',
				title: 'Hata',
				text: 'Lütfen sadece resim dosyası seçiniz!',
				showConfirmButton: false,
			});
		}
		else {
			setProfilePhoto(file);
			await handleUpdateProfile(e);
		}
	};

	const handleCancelRequest = async () => {
		await Swal.fire({
			icon: 'warning',
			title: 'Emin misiniz?',
			text: 'Profil fotoğrafı güncelleme isteğinizi iptal etmek istediğinize emin misiniz?',
			showCancelButton: true,
			confirmButtonText: 'Evet',
			cancelButtonText: 'Hayır',
		}).then(async (result) => {
			if (result.isConfirmed) {
				const response = await request(`/user/avatar/${statusText.id}/cancel`, 'POST', null, true, null, true, 500);
				if (response.success) {
					await Swal.fire({
						icon: 'success',
						title: 'Başarılı',
						text: response.message,
						showConfirmButton: false,
						timer: 1500,
					});
					setStatusText({});
				}
			}
		});

	};

	useEffect(() => {
		if (profilePhoto) {
			const reader = new FileReader();
			reader.onloadend = () => {
				setPreview(reader.result);
			};
			reader.readAsDataURL(profilePhoto);
		}
		else {
			setPreview(null);
		}
	}, [profilePhoto]);

	useEffect(() => {
		const getAvatarStatus = async () => {
			const {success, message, data} = await request('/user/avatar/status', 'GET', null, true, null, true, 500);
			if (success) {
				setStatusText({
					message,
					id: data.id,
				});
			}
		};
		getAvatarStatus();
	}, []);

	return (
		<div className="bg-white dark:bg-jacarta-700 rounded-lg shadow-md p-6">
			<div className="flex flex-col sm:flex-row gap-6">
				<div className="flex justify-center">
					<form encType="multipart/form-data" className="relative w-8/12 inline-block">
						<Image
							src={preview ? preview : `https://cdn.tevkilapp.com/${(user.user ? user.user.avatar : 'images/user/user_avatar.gif')}`}
							alt="collection avatar"
							className="dark:border-jacarta-600 rounded-xl border-[5px] border-white"
							height={440}
							width={440}
						/>
						<div
							className={`group hover:bg-accent border-jacarta-100 absolute right-0 bottom-0 h-8 w-8 overflow-hidden rounded-full border bg-white text-center hover:border-transparent ${loading && '!bg-accent'}`}>
							<input
								type="file"
								accept="image/*"
								disabled={loading}
								className="absolute top-0 left-0 w-full cursor-pointer opacity-0"
								onChange={(e) => handleProfilePhoto(e)}
							/>
							<div className="flex h-full items-center justify-center">
								{loading ? (
									<LoaderComponent/>
								) : (
									<svg
										xmlns="http://www.w3.org/2000/svg"
										viewBox="0 0 24 24"
										width="24"
										height="24"
										className="fill-jacarta-400 h-4 w-4 group-hover:fill-white"
									>
										<path fill="none" d="M0 0h24v24H0z"/>
										<path
											d="M15.728 9.686l-1.414-1.414L5 17.586V19h1.414l9.314-9.314zm1.414-1.414l1.414-1.414-1.414-1.414-1.414 1.414 1.414 1.414zM7.242 21H3v-4.243L16.435 3.322a1 1 0 0 1 1.414 0l2.829 2.829a1 1 0 0 1 0 1.414L7.243 21z"/>
									</svg>
								)}
							</div>
						</div>
					</form>
				</div>

				<div className=" mt-3">
					<p className="dark:text-jacarta-200 text-jacarta-400 font-medium text-sm">
						Profil resminizi değiştirmek için sol taraftaki butona basabilirsiniz. Resminizi değiştirdikten sonra
						profil resminizi güncellemek istediğinize dair yöneticilere bilgi verilecektir. Yöneticilerin onaylama
						süreci sonrasında profil resminiz güncellenecektir.
					</p>
				</div>
			</div>
			<div className="mt-3 w-full">
				{statusText.id && (
					<div className="bg-red-700 p-2 flex gap-4 items-center rounded-2lg">
						<span className="dark:text-gray-200 text-jacarta-50  font-body text-sm">{statusText.message}</span>
						<svg onClick={handleCancelRequest} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 cursor-pointer text-jacarta-50">
							<path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12"/>
						</svg>
					</div>
				)}
			</div>
		</div>
	);
};

export default ChangeAvatarContainer;