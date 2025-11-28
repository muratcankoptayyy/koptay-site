import React, {useEffect, useState} from 'react';
import Meta from '@/components/Meta';
import Image from 'next/image';
import {useRouter} from 'next/router';
import request from '@/utils/request';
import LoaderComponent from '@/components/LoaderComponent';
import Swal from 'sweetalert2';
import {Autocomplete, Box, Button, TextField} from '@mui/material';
import introJs from 'intro.js';
import {PhoneVerificationModal} from '@/components/modals/PhoneVerificationModal';

function TaskCreate() {
	const router = useRouter();

	const [loading, setLoading] = React.useState(false);
	const [citiesOptions, setCitiesOptions] = React.useState([]);
	const [districtsOptions, setDistrictsOptions] = React.useState([]);
	const [taskTitle, setTaskTitle] = React.useState([]);
	const [options, setOptions] = React.useState([]);
	const [phoneValue, setPhoneValue] = React.useState('');
	const [form, setForm] = React.useState({
		datetime: '', type: 0, content: '', price: '0.00', title_id: 0,
	});
	const [isModalOpen, setModalOpen] = useState(false);

	const handleGetDistricts = async (city_id) => {
		setDistrictsOptions([]);
		setForm({
			...form,
			city_id: Number(city_id),
			district_id: null
		});
		const response = await request(`/city/${city_id}`, 'GET', null, null, null);
		const optionsData = response.data.districts.map((district) => ({ label: district.name, key: district.id }));

		setDistrictsOptions(optionsData);
	};

	const handleGetTaskTitle = async (task_title_id) => {
		setForm({...form, type: Number(task_title_id), price: '0.00'});
		const response = await request(`/task/title`, 'POST', {
			type: task_title_id,
		}, true, null);
		setTaskTitle(response.data);
	};

	const handleCreateTask = async (e) => {
		e.preventDefault();
		setLoading(true);

		try {
			// Formatlı numarayı temizle
			const cleanPhone = form.phone.replace(/\D/g, '');
			
			// Telefon numarası doğrulama kontrolü
			const checkResponse = await request('/phone/verify', 'POST', {
				action: 'check',
				phone: cleanPhone
			}, true);

			if (checkResponse.success) {
				if (checkResponse.is_verified) {
					// Telefon zaten doğrulanmış, direkt form gönder
					await proceedWithTaskCreation();
				} else {
					// Telefon doğrulanmamış, kod gönder
					const sendResponse = await request('/phone/verify', 'POST', {
						action: 'send',
						phone: cleanPhone
					}, true);

					if (sendResponse.success) {
						setModalOpen(true);
					} else {
						await Swal.fire({
							icon: 'error',
							title: 'Hata!',
							text: sendResponse.error || 'Doğrulama kodu gönderilemedi.',
						});
					}
				}
			} else {
				await Swal.fire({
					icon: 'error',
					title: 'Hata!',
					text: checkResponse.error || 'Telefon doğrulama kontrolü başarısız oldu.',
				});
			}
		} catch (error) {
			await Swal.fire({
				icon: 'error',
				title: 'Hata!',
				text: 'Bir hata oluştu. Lütfen tekrar deneyin.',
			});
		}

		setLoading(false);
	};

	const proceedWithTaskCreation = async () => {
		const {success, error, message} = await request('/new/tasks', 'POST', form, false, null);
		
		if (success) {
			await Swal.fire({
				icon: 'success',
				title: 'Başarılı!',
				text: message,
				confirmButtonText: 'Tamam',
				timer: 2000,
			});
			setForm({
				datetime: '',
				type: 0,
				content: '',
				price: '0.00',
				title_id: 0,
				name: '',
				phone: ''
			});
			setPhoneValue('');
			setTaskTitle([]);
			window.location.reload();
		} else {
			await Swal.fire({
				icon: 'error',
				title: 'Hata!',
				text: error,
				confirmButtonText: 'Tamam',
			});
		}
	};

	const handleVerified = async () => {
		setModalOpen(false);
		await proceedWithTaskCreation();
	};

	const handleChangeTaskTitle = (e) => {
		const findMinPrice = taskTitle.find((task) => task.id === Number(e.target.value));
		if (findMinPrice === undefined) {
			setForm({...form, title_id: 0, price: '0.00'});
		}
		else {
			setForm({...form, title_id: Number(e.target.value), price: Number(findMinPrice.min_price)});
		}
	};

	const formatPhoneNumber = (value) => {
		// Sadece rakamları al
		const numericValue = value.replace(/\D/g, '');
		
		// Maksimum 10 rakam olsun
		if (numericValue.length > 11) return phoneValue;
		
		// Boş ise boş döndür
		if (numericValue.length === 0) return '';

		// Eğer 0 ile başlıyorsa onu kullan, başlamıyorsa 0 ekle
		const withZero = numericValue.startsWith('0') ? numericValue : '0' + numericValue;
		
		if (withZero.length <= 1) return withZero;
		if (withZero.length <= 5) return `${withZero[0]} (${withZero.slice(1)}`;
		if (withZero.length <= 8) return `${withZero[0]} (${withZero.slice(1, 4)}) ${withZero.slice(4)}`;
		if (withZero.length <= 10) return `${withZero[0]} (${withZero.slice(1, 4)}) ${withZero.slice(4, 7)} ${withZero.slice(7)}`;
		return `${withZero[0]} (${withZero.slice(1, 4)}) ${withZero.slice(4, 7)} ${withZero.slice(7, 9)} ${withZero.slice(9)}`;
	};

	const handlePhoneChange = (event) => {
		const formattedValue = formatPhoneNumber(event.target.value);
		setPhoneValue(formattedValue);
		// Sadece rakamları al ve başındaki 0'ı kaldır
		const numericValue = formattedValue.replace(/\D/g, '');
		const phoneWithoutZero = numericValue.startsWith('0') ? numericValue.slice(1) : numericValue;
		setForm({...form, phone: phoneWithoutZero});
	};

	const viewTour = () => {
		introJs().setOptions({
			nextLabel: 'İleri',
			prevLabel: 'Geri',
			doneLabel: 'Bitir',
		}).start();
		// introJs()
	}

	useEffect(() => {
		const getAllCities = async () => {
			const response = await request('/city', 'GET', null, null, null, true, 160);
			const optionsData = response.data.map((city) => ({label: city.name, key: city.id}));
			setCitiesOptions(optionsData);
		};

		const getAllCourthouses = async () => {
			const response = await request('/courthouses', 'GET', null, null, null, true, 160);

			const optionsData = response.data.map((courthouse) => ({label: courthouse.name, key: courthouse.id}));
			setOptions(optionsData);
		};

		getAllCities();
		getAllCourthouses();
	}, []);

	return (<>
			<Meta title="Görev Oluştur"/>
			<section className="relative pt-16 lg:pb-12 pb-0">
				<picture className="pointer-events-none absolute inset-x-0 top-0 -z-10 dark:hidden">
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

				<div className="py-16 md:py-24">
					<div className="container">
						<div className="mb-8 pb-px">
							<div className="flex flex-col md:flex-row gap-4 md:gap-0 justify-between">
								<div>
									<h1 className="pt-3 mb-0 font-display text-2xl font-medium text-jacarta-700 dark:text-white">
										Hızlı Yeni Tevkil Oluştur
									</h1>
									<p className="dark:text-jacarta-100 font-medium text-2xs">
										Tevkilapp platformu için yeni bir tevkil oluştur.
									</p>
								</div>
								<div className="flex items-center">
									<button className="bg-blue-200/80 rounded-full text-blue-800 p-2 px-8 w-full md:w-auto font-semibold hover:bg-blue-600 hover:text-white transition-all duration-200 hover:shadow-lg flex items-center gap-2 justify-center sm:justify-start" onClick={(e) => viewTour()}>
									<svg xmlns="http://www.w3.org/2000/svg" width={18} height={18} viewBox="0 0 24 24"><mask id="lineMdFilePlusFilled0"><g fill="none" stroke="#fff" strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}><path fill="#fff" fillOpacity={0} strokeDasharray={64} strokeDashoffset={64} d="M13.5 3l5.5 5.5v11.5c0 0.55 -0.45 1 -1 1h-12c-0.55 0 -1 -0.45 -1 -1v-16c0 -0.55 0.45 -1 1 -1Z"><animate fill="freeze" attributeName="fill-opacity" begin="0.6s" dur="0.5s" values="0;1"></animate><animate fill="freeze" attributeName="stroke-dashoffset" dur="0.6s" values="64;0"></animate></path><path fill="#000" stroke="#000" d="M14.5 3.5l0 4.5l4.5 0z" opacity={0}><set fill="freeze" attributeName="opacity" begin="0.6s" to={1}></set></path><path d="M13.5 3l5.5 5.5" opacity={0}><set fill="freeze" attributeName="opacity" begin="0.6s" to={1}></set></path><path fill="#000" fillOpacity={0} stroke="none" d="M19 13c3.31 0 6 2.69 6 6c0 3.31 -2.69 6 -6 6c-3.31 0 -6 -2.69 -6 -6c0 -3.31 2.69 -6 6 -6Z"><set fill="freeze" attributeName="fill-opacity" begin="1.1s" to={1}></set></path><path strokeDasharray={8} strokeDashoffset={8} d="M16 19h6"><animate fill="freeze" attributeName="stroke-dashoffset" begin="1.1s" dur="0.2s" values="8;0"></animate></path><path strokeDasharray={8} strokeDashoffset={8} d="M19 16v6"><animate fill="freeze" attributeName="stroke-dashoffset" begin="1.3s" dur="0.2s" values="8;0"></animate></path></g></mask><rect width={24} height={24} fill="currentColor" mask="url(#lineMdFilePlusFilled0)"></rect></svg>
									Tevkil Nasıl Oluşturulur?
									</button>
								</div>
							</div>
							<div className="mt-4 p-4 bg-blue-50 dark:bg-jacarta-700 rounded-lg">
								<p className="text-blue-800 dark:text-white text-sm">
									Tevkilapp, yenilikçi altyapısıyla sizi kayıt süreçleriyle uğraştırmadan, sadece birkaç tıklamayla hızlı ve güvenli bir şekilde tevkil görevi oluşturma imkanı sunar.
								</p>
								<p className="text-blue-600 dark:text-jacarta-200 text-sm mt-2">
									Bu sayfa üzerinden Tevkilapp&apos;e kayıt olmadan hızlı bir şekilde tevkil oluşturabilirsiniz.
								</p>
							</div>
						</div>
						<form onSubmit={handleCreateTask}>
							<div className="mb-6">
								<label
									htmlFor="name"
									className="font-display text-jacarta-700 mb-0 block dark:text-white"
								>
									İsim Soyisim <span className="text-red-500">*</span>
								</label>
								<input
									type="text"
									id="name"
									name="name"
									data-intro="Bu alana isim soyisminizi yazınız."
									placeholder="Bu alana isim soyisminizi yazınız."
									className="px-5 dark:bg-jacarta-700 border-jacarta-100 hover:ring-accent/10 focus:ring-accent dark:border-jacarta-600 dark:placeholder:text-jacarta-300 w-full rounded-lg py-3 px-3 hover:ring-2 dark:text-white"
									required
									autoComplete="name"
									onChange={(e) => setForm({...form, name: e.target.value})}
								/>
							</div>
							<div className="mb-6">
								<label
									htmlFor="phone"
									className="font-display text-jacarta-700 mb-0 block dark:text-white"
								>
									Telefon Numarası <span className="text-red-500">*</span>
								</label>
								<input
									type="text"
									id="phone"
									value={phoneValue}
									onChange={handlePhoneChange}
									placeholder="0 (5XX) XXX XX XX"
									data-intro="Bu alana telefon numaranızı yazınız."
									maxLength="17"
									autoComplete="tel"
									className="px-5 dark:bg-jacarta-700 border-jacarta-100 hover:ring-accent/10 focus:ring-accent dark:border-jacarta-600 dark:placeholder:text-jacarta-300 w-full rounded-lg py-3 px-3 hover:ring-2 dark:text-white"
									required
								/>
							</div>

							<div className="mb-6">
								<label
									htmlFor="datetime"
									className="font-display text-jacarta-700 mb-0 block dark:text-white"
								>
									Görevin Yapılacağı Tarih <span className="text-red-500">*</span>
								</label>
								<p className="mb-3 text-jacarta-500 text-sm dark:text-jacarta-300">Görevin
									yapılacağı tarihi giriniz.<span
										className={"text-black block dark:text-white font-bold "}></span></p>
								<input
									type="datetime-local"
									id="datetime"
									name="datetime"
									data-intro="Bu alana görevin yapılacağı tarihi giriniz."
									className="px-5 dark:bg-jacarta-700 border-jacarta-100 hover:ring-accent/10 focus:ring-accent dark:border-jacarta-600 dark:placeholder:text-jacarta-300 w-full rounded-lg py-3 px-3 hover:ring-2 dark:text-white"
									required
									onChange={(e) => setForm({...form, datetime: e.target.value})}
								/>
							</div>

							<div className="mb-6">
								<label
									htmlFor="task-type"
									className="font-display text-jacarta-700 mb-2 block dark:text-white"
								>
									Görev Tipi<span className="text-red-500">*</span>
								</label>
								<div className="flex gap-4 w-full sm:w-1/3" data-intro="Lütfen görevinizin adliye içinde mi yoksa adliye dışındamı yapılacağını seçiniz. Daha sonrasında görev tipine göre adliye veya il & ilçe seçimi yapınız.">
									<button
										type="button"
										onClick={() => handleGetTaskTitle("1")}
										className={`flex items-center justify-center gap-3 flex-1 py-4 px-6 rounded-xl bg-white/40 border-2 transition-all duration-200 ${
											form.type === 1
												? "border-blue-600 bg-blue-600/20 dark:bg-blue-600/20 text-blue-600"
												: "border-jacarta-100 dark:border-jacarta-600 text-jacarta-700 dark:text-white hover:border-blue-600 hover:bg-blue-600/20 dark:hover:bg-blue-600/20 hover:text-blue-600"
										}`}
									>
										<svg xmlns="http://www.w3.org/2000/svg" width={24} height={24} viewBox="0 0 24 24"><path fill="currentColor" d="M9 4.765V20h2v-5h2v5h2V4.766A6.2 6.2 0 0 0 12 4c-1.089 0-2.11.277-3 .765m8 1.616v3.72A6.98 6.98 0 0 1 22 8h1v14H1V8h1c1.959 0 3.73.804 5 2.101v-3.72l-.033.03l-1.379-1.448l.724-.69q.526-.5 1.136-.904A8.2 8.2 0 0 1 12 2a8.22 8.22 0 0 1 5.69 2.276l.724.69l-1.38 1.448zM7 15a5 5 0 0 0-4-4.9V20h4zm10 5h4v-9.9a5 5 0 0 0-4 4.9zM11 6.998h2.004v2.004H11z"></path></svg>
										<span className="font-display text-base font-semibold">Adliye İçi</span>
									</button>
									<button
										type="button"
										onClick={() => handleGetTaskTitle("2")}
										className={`flex items-center justify-center gap-3 flex-1 py-4 px-6 rounded-xl bg-white/40 border-2 transition-all duration-200 ${
											form.type === 2
												? "border-accent bg-accent/20 dark:bg-accent/20 text-accent"
												: "border-jacarta-100 dark:border-jacarta-600 text-jacarta-700 dark:text-white hover:border-accent hover:bg-accent/20 dark:hover:bg-accent/20 hover:text-accent"
										}`}
									>
										<svg xmlns="http://www.w3.org/2000/svg" width={24} height={24} viewBox="0 0 16 16"><path fill="currentColor" d="M14.63 7L13 3h1V2H9V1H8v1H3v1h1L2.38 7H2v1h.15c.156.498.473.93.9 1.23a2.47 2.47 0 0 0 2.9 0A2.44 2.44 0 0 0 6.86 8H7V7h-.45L4.88 3H8v8H6l-.39.18l-2 2.51l.39.81h9l.39-.81l-2-2.51L11 11H9V3h3.13l-1.67 4H10v1h.15a2.48 2.48 0 0 0 4.71 0H15V7zM5.22 8.51a1.5 1.5 0 0 1-.72.19a1.45 1.45 0 0 1-.71-.19A1.5 1.5 0 0 1 3.25 8h2.5a1.5 1.5 0 0 1-.53.51M5.47 7h-2l1-2.4zm5.29 5L12 13.5H5L6.24 12zm1.78-7.38l1 2.4h-2zm.68 3.91a1.4 1.4 0 0 1-.72.19a1.35 1.35 0 0 1-.71-.19a1.55 1.55 0 0 1-.54-.53h2.5a1.37 1.37 0 0 1-.53.53"></path></svg>
										<span className="font-display text-base font-semibold">Adliye Dışı</span>
									</button>
								</div>
							</div>

							<div className="mb-6">
								<label
									htmlFor="task_title"
									className="font-display text-jacarta-700 mb-2 block dark:text-white"
								>
									Görev İçeriği <span className="text-red-500">*</span>
								</label>
								<Autocomplete
									id="task_title"
									options={taskTitle ? taskTitle.map(task => ({
										label: task.name,
										key: task.id
									})) : []}
									disabled={taskTitle && taskTitle.length === 0}
									renderInput={(params) => (
										<TextField
											{...params}
											label="Görev İçeriği Seçiniz"
											required
										/>
									)}
									onChange={(e, value) => value && handleChangeTaskTitle({ target: { value: value.key } })}
									renderOption={(props, option) => (
										<Box component="li" {...props} key={option.key}>
											{option.label}
										</Box>
									)}
									data-intro="Görev tipine göre görev içeriğini seçiniz."
								/>
							</div>

							<div>
								{form.type === 2 && (<>
									<div className="flex mb-6 gap-7">
										<div className="w-1/2">
											<label
												htmlFor="task_title"
												className="font-display text-jacarta-700 mb-2 block dark:text-white"
											>
												Şehir <span className="text-red-500">*</span>
											</label>
											<Autocomplete
												autoHighlight
												getOptionLabel={(option) => option.label}
												onChange={(e, value) => handleGetDistricts(value.key)}
												renderOption={(props, option) => (
													<Box component="li" {...props} key={option.key}>
														{option.label}
													</Box>
												)}
												renderInput={(params) => (
													<TextField
														{...params}
														label="Şehir Seçiniz"
														inputProps={{
															...params.inputProps,
															autoComplete: 'new-password', // disable autocomplete and autofill
														}}
													/>
												)}
												options={citiesOptions}/>

										</div>
										<div className="w-1/2">
											<label
												htmlFor="task_title"
												className="font-display text-jacarta-700 mb-2 block dark:text-white"
											>
												İlçe <span className="text-red-500">*</span>
											</label>
											<Autocomplete
												disabled={districtsOptions.length === 0}
												autoHighlight
												value={districtsOptions.find((option) => option.key === form.district_id) || null}
												onChange={(e, value) => setForm({...form, district_id: value.key})}
												renderOption={(props, option) => (
													<Box component="li" {...props} key={option.key}>
														{option.label}
													</Box>
												)}
												renderInput={(params) => (
													<TextField
														{...params}
														label="İlçe Seçiniz"
														inputProps={{
															...params.inputProps,
														}}
													/>
												)}
												options={districtsOptions}/>
										</div>
									</div>
								</>)}
								{form.type === 1 && (<div className="w-full mb-6">
									<label
										htmlFor="task_title"
										className="font-display text-jacarta-700 mb-2 block dark:text-white"
									>
										Adliye <span className="text-red-500">*</span>
									</label>
									<Autocomplete
										data-intro="Adliye seçiminizi yapınız."
										sx={{
											width: '100%',
											bgcolor: '#131740',
											'& .MuiOutlinedInput-root .MuiOutlinedInput-notchedOutline': {
												borderColor: 'transparent',
											},
											'& .css-nxo287-MuiInputBase-input-MuiOutlinedInput-input': {
												color: 'red',
											},
										}}
										autoHighlight
										getOptionLabel={(option) => option.label}
										onChange={(e, value) => {
											setForm({...form, courthouse_id: value.key});
										}}
										renderOption={(props, option) => (
											<Box component="li" {...props} key={option.key}>
												{option.label}
											</Box>
										)}
										renderInput={(params) => (
											<TextField
												{...params}
												label="Adliye Seçiniz"
												inputProps={{
													...params.inputProps,
													autoComplete: 'new-password', // disable autocomplete and autofill
												}}
											/>
										)}
										options={options}/>
								</div>)}
							</div>
							<div className="mb-6">
								<label
									htmlFor="price"
									className="font-display text-jacarta-700 mb-0 block dark:text-white"
								>
									Görev Ücreti (₺) <span className="text-red-500">*</span>
								</label>
								<p className="mb-3 text-jacarta-500 text-sm dark:text-jacarta-300">Bu alanda lütfen
									görevi tamamlayan kişiye ödeyeceğiniz tutarı ₺ olarak belirtin.</p>
								<input
									id="price"
									name="price"
									type="text"
									className="px-5 dark:bg-jacarta-700 border-jacarta-100 hover:ring-accent/10 focus:ring-accent dark:border-jacarta-600 dark:placeholder:text-jacarta-300 w-full rounded-lg py-3  hover:ring-2 dark:text-white"
									value={form.price > 0 ? form.price : ''}
									placeholder={`0.00`}
									pattern="[0-9,.]*"
									data-intro="Görev tamamlandığında ödeyecek olduğunuz ücreti yazınız."
									onChange={(e) => setForm({...form, price: e.target.value})}
									required
									disabled={form.title_id === 0}
								/>
							</div>
							<div className="mb-6">
								<label
									htmlFor="content"
									className="font-display text-jacarta-700 mb-0 block dark:text-white"
								>
									Görev Açıklaması <span className="text-red-500">*</span>
								</label>
								<p className="mb-3 text-jacarta-500 text-sm dark:text-jacarta-300">Görevlendirilecek
									kişinin yapacağı işlemleri lütfen detaylı şekilde belirtin.</p>
								<textarea
									name="content"
									id="content"
									className="px-5 dark:bg-jacarta-700 border-jacarta-100 hover:ring-accent/10 focus:ring-accent dark:border-jacarta-600 dark:placeholder:text-jacarta-300 w-full rounded-lg py-3  hover:ring-2 dark:text-white"
									placeholder="Görev açıklamanızı bu alana yazınız."
									rows="7"
									data-intro="Bu alana görev tarihi ve göreviniz ile alakalı tüm diğer detayları yazınız."
									required
									onChange={(e) => setForm({...form, content: e.target.value})}
								></textarea>
							</div>
							<div className="mb-6">
								<label>
									<input type="checkbox"
										   data-intro="Bilgileri doldurduktan sonra görev oluşturma kurallarını okuyunuz ve ilerleyebilmek için onaylayınız."
										   required
										   className="form-checkbox h-5 w-5 text-jacarta-600 dark:text-jacarta-600"/>
									<span className="ml-2 text-jacarta-700 dark:text-white">TevkilApp platformu görev oluşturma ve <a className="text-blue-500" target="_blank" href='https://www.tevkilapp.com/sayfa/kvkk-aydinlatma-metni'>kişisel verilerimin işlenmesine</a>  dair kuralları okudum kabul ediyorum..</span>
								</label>
							</div>
							<button
								type="submit"
								data-intro="Tüm işlemleri tamamladıktan sonra görev oluştur butonuna tıklayınız."
								disabled={loading}
								className="bg-accent shadow-accent-volume hover:bg-accent-hover text-white font-bold py-3 px-8 rounded-xl w-full transition-colors"
							>
								{loading ? (<LoaderComponent/>) : 'Görev Oluştur'}
							</button>
						</form>
					</div>
				</div>
			</section>
			<PhoneVerificationModal
				isOpen={isModalOpen}
				onClose={() => setModalOpen(false)}
				phone={phoneValue}
				onVerified={handleVerified}
			/>
		</>
	);
};

export default TaskCreate;