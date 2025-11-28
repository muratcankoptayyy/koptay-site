import Image from 'next/image';
import React, {useState} from 'react';
import ModalVideo from 'react-modal-video';
import request from '../../utils/request';

const Promo = () => {
	const [videoModal, setvideoModal] = useState(false);
	const [url, setUrl] = useState(null);

	const [promoText, setPromoText] = useState('');

	const fetchData = async () => {
		const {data, success} = await request('/page/agreements', 'GET', null, true, false, true, 0);
		if (success) {
			setPromoText(data.content);
		}
	};

	React.useEffect(() => {
		fetchData();
	});

	return (
		<>
			{/* <!-- Promo --> */}
			<section className="relative py-24 dark:bg-jacarta-800">
				<picture className="pointer-events-none absolute inset-0 -z-10 dark:hidden">
					<Image
						width={1519}
						height={773}
						priority
						src="https://cdn.tevkilapp.com/images/gradient_light.jpg"
						alt="gradient"
						className="h-full w-full object-cover"
					/>
				</picture>
				<div className="container">
					<div className="lg:flex lg:justify-between">
						{/* <!-- Image --> */}
						<div className="relative lg:w-[55%] flex justify-center items-center">
							<Image
								width={68}
								height={68}
								src="https://cdn.tevkilapp.com/images/patterns/pattern_circle_1.png"
								className="absolute -bottom-4 -left-8 animate-fly dark:opacity-10"
								alt="circle"
							/>
							<Image
								width={143}
								height={143}
								src="https://cdn.tevkilapp.com/images/patterns/pattern_circle_2.png"
								className="absolute -top-14 right-0 animate-fly dark:opacity-10 md:-right-12"
								alt="circle"
							/>
							<div className="flex items-center space-x-7">
								<figure className="relative">
									<Image
										width={308}
										height={452}
										src="https://cdn.tevkilapp.com/uploads/tevkilapp-promo-1.png"
										className="rounded-3xl w-full h-full object-cover"
										alt="promo"
									/>
								</figure>
								<figure className="relative overflow-hidden rounded-3xl before:absolute before:bg-jacarta-900/25">
									<Image
										width={308}
										height={471}
										src="https://cdn.tevkilapp.com/uploads/tevkilapp-promo-2.png"
										className="w-full h-full object-cover"
										alt="img"
									/>
								</figure>
							</div>
						</div>

						{/* <!-- Info --> */}
						<div className="py-10 lg:w-[45%] lg:pl-28">
							{/*{{ promoText }}*/}
							<h2 className="mb-6 font-display text-3xl text-jacarta-700 dark:text-white">
								TevkilApp&apos;e İlk Adım
							</h2>
							<p className="mb-8 text-lg leading-normal dark:text-jacarta-300">
								TevkilApp ile işlerinizi kolaylaştırın. İşlerinizi kolaylaştırmak için aşağıdaki adımları takip edin.
							</p>

							<div className="mb-8 flex space-x-4">
								<svg className="h-8 w-8 shrink-0 fill-accent text-accent" xmlns="http://www.w3.org/2000/svg" width={24} height={24} viewBox="0 0 32 32"><path fill="currentColor" d="M14 4c-3.854 0-7 3.146-7 7c0 2.41 1.23 4.552 3.094 5.813C6.527 18.343 4 21.88 4 26h2c0-4.43 3.57-8 8-8c1.376 0 2.654.358 3.78.97A8 8 0 0 0 16 24c0 4.406 3.594 8 8 8s8-3.594 8-8s-3.594-8-8-8a7.98 7.98 0 0 0-4.688 1.53c-.442-.277-.92-.51-1.406-.718A7.02 7.02 0 0 0 21 11c0-3.854-3.146-7-7-7m0 2c2.773 0 5 2.227 5 5s-2.227 5-5 5s-5-2.227-5-5s2.227-5 5-5m10 12c3.326 0 6 2.674 6 6s-2.674 6-6 6s-6-2.674-6-6s2.674-6 6-6m-1 2v3h-3v2h3v3h2v-3h3v-2h-3v-3z"></path></svg>
								<div>
									<span className="mb-1 block font-display text-md font-semibold text-jacarta-700 dark:text-white">
									Hemen Giriş Yapın
									</span>
									<span className="dark:text-jacarta-300 text-base">
									  TevkilApp&apos;e kayıt olmanız gerek yok, telefon numaranız ile hızlıca giriş yapabilirsiniz.
									</span>
								</div>
							</div>

							<div className="mb-8 flex space-x-4">
								<svg className="h-8 w-8 shrink-0 fill-accent text-accent" xmlns="http://www.w3.org/2000/svg" width={24} height={24} viewBox="0 0 24 24"><g fill="none"><circle cx={12} cy={9} r={3} fill="currentColor"></circle><path fill="currentColor" fillRule="evenodd" d="M17.451 15.908a.24.24 0 0 1-.067.304A8.96 8.96 0 0 1 12 18a8.96 8.96 0 0 1-5.384-1.788a.24.24 0 0 1-.067-.304C7.499 14.192 9.582 13 12 13s4.501 1.191 5.451 2.908" clipRule="evenodd"></path><path stroke="currentColor" strokeLinecap="round" strokeWidth={2} d="M17 4h.502c1.211 0 1.817 0 2.281.232a2.2 2.2 0 0 1 .985.985C21 5.68 21 6.287 21 7.498V8m-4 12h.502c1.211 0 1.817 0 2.281-.232a2.2 2.2 0 0 0 .985-.985c.232-.464.232-1.07.232-2.281V16M7 4h-.502c-1.211 0-1.817 0-2.281.232a2.2 2.2 0 0 0-.985.985C3 5.68 3 6.287 3 7.498V8m4 12h-.502c-1.211 0-1.817 0-2.281-.232a2.2 2.2 0 0 1-.985-.985C3 18.32 3 17.713 3 16.502V16"></path></g></svg>
								<div>
									<span className="mb-1 block font-display text-md font-semibold text-jacarta-700 dark:text-white">
									Profilinizi Doğrulayın
									</span>
									<span className="dark:text-jacarta-300">
									Kişiselleştirme ayarlarınızı yapın ve Avukat profilinizi tamamlayın.
									</span>
								</div>
							</div>

							<div className="text-center mb-6 text-uppercase font-semibold text-sm text-jacarta-500">Artık TevkilApp&apos;de Aşağıdaki Özellikleri Kullanabilirsiniz</div>

							<div className="mb-8 flex space-x-4">
								<svg className="h-8 w-8 shrink-0 fill-accent text-accent" xmlns="http://www.w3.org/2000/svg" width={24} height={24} viewBox="0 0 24 24"><path fill="currentColor" d="M13.09 20c.12.72.37 1.39.72 2H6c-1.11 0-2-.89-2-2V4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v9.09c-.33-.05-.66-.09-1-.09s-.67.04-1 .09V4h-5v8l-2.5-2.25L8 12V4H6v16zM20 18v-3h-2v3h-3v2h3v3h2v-3h3v-2z"></path></svg>
								<div>
									<span className="mb-1 block font-display text-md font-semibold text-jacarta-700 dark:text-white">
									Ücretsiz Tevkil Oluştur
									</span>
									<span className="dark:text-jacarta-300">
									Tevkil Görevi Oluşturmak <u>ücretsizdir</u>. Ancak TevkilApp&apos;in güncel tevkil piyasasına göre belirlediği tarifenin altında ilan oluşturulamaz.
									</span>
								</div>
							</div>

							
							<div className="mb-8 flex space-x-4">
								<svg className="h-8 w-8 shrink-0 fill-accent text-accent" xmlns="http://www.w3.org/2000/svg" width={24} height={24} viewBox="0 0 24 24"><g fill="none" stroke="currentColor" strokeWidth={2}><path d="M12 4C8.229 4 6.343 4 5.172 5.172S4 8.229 4 12v6c0 .943 0 1.414.293 1.707S5.057 20 6 20h6c3.771 0 5.657 0 6.828-1.172S20 15.771 20 12"></path><path strokeLinecap="round" strokeLinejoin="round" d="M9 10h6m-6 4h3m7-6V2m-3 3h6"></path></g></svg>
								<div>
									<span className="mb-1 block font-display text-md font-semibold text-jacarta-700 dark:text-white">
										Görev Sıralarına Katıl ve Tevkil Almaya Başla
									</span>
									<span className="dark:text-jacarta-300">
									Tevkil görevlendirmesi almak istediğiniz ilçe ve adliyeleri seçin ve açılan Tevkil görevlerine başvurun. Tevkil görevlenerine başvurabilmek için Barokart onayı yapmanız gerekmektedir.
									</span>

									<div class="mt-4 bg-blue-50 border border-blue-200 text-sm text-blue-600 rounded-lg p-4 dark:bg-white/10 dark:border-white/10 dark:text-neutral-400" role="alert" tabindex="-1" aria-labelledby="hs-link-on-right-label">
										<div class="flex items-center">
											<div class="shrink-0">
											<svg className="shrink-0 size-4 mt-0.5" xmlns="http://www.w3.org/2000/svg" width={24} height={24} viewBox="0 0 16 16"><path fill="currentColor" d="M3.5 2a.5.5 0 0 0-.447.276l-2 4a.5.5 0 0 0 .059.54l4.907 6.039A3 3 0 0 1 6 12.5c0-.355.074-.693.208-.999L2.55 7h2.583l1.285 4.115c.209-.312.485-.575.809-.767L6.18 7h1.49a3 3 0 0 1 .594-1H6.14l.75-3h2.22l.53 2.125a3 3 0 0 1 1.001-.122L10.141 3h2.05l1.5 3h-.955c.258.289.462.627.593 1h.12l-.085.105a3 3 0 0 1 .077 1.492l1.447-1.782a.5.5 0 0 0 .06-.539l-2-4A.5.5 0 0 0 12.5 2zM2.309 6l1.5-3h2.05l-.75 3zM12.5 8a2 2 0 1 1-4 0a2 2 0 0 1 4 0m1.5 4.5c0 1.245-1 2.5-3.5 2.5S7 13.75 7 12.5A1.5 1.5 0 0 1 8.5 11h4a1.5 1.5 0 0 1 1.5 1.5"></path></svg>
											</div>
											<div class="flex-1 md:flex md:justify-between ms-4">
											<p id="hs-link-on-right-label" class="text-sm">
											Yeni üyelerimize özel Ücretsiz Premium hakkınızı almayı unutmayın!
											<br/>
											<a href="#" class="text-blue-600 hover:text-blue-700 focus:outline-hidden focus:text-blue-700 font-medium whitespace-nowrap dark:text-neutral-200 dark:hover:text-neutral-400 dark:focus:text-neutral-400">Detaylı bilgi için tıklayınız</a>
											</p>
											</div>
										</div>
									</div>
								</div>
							</div>


						</div>
					</div>
				</div>
			</section>
			{/* <!-- end promo --> */}

			{/* <!-- YouTube Video Modal --> */}
			<div
				className={
					videoModal ? 'modal lightbox fade show block' : 'modal lightbox fade'
				}
			>
				<div className="modal-dialog modal-dialog-centered modal-xl w-full">
					<div className="modal-content border-0 bg-transparent">
						<div className="modal-body p-0 relative">
							<button
								onClick={() => {
									setvideoModal(false);
									setUrl(null);
								}}
								type="button"
								className="btn-close position-absolute top-0 end-0 p-3 z-10"
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 16 16"
									fill="#fff"
									className="h-6 w-6"
								>
									<path d="M.293.293a1 1 0 011.414 0L8 6.586 14.293.293a1 1 0 111.414 1.414L9.414 8l6.293 6.293a1 1 0 01-1.414 1.414L8 9.414l-6.293 6.293a1 1 0 01-1.414-1.414L6.586 8 .293 1.707a1 1 0 010-1.414z"></path>
								</svg>
							</button>
							<div
								id="lightboxCarousel-d7ewe4ig"
								className="lightbox-carousel carousel"
							>
								<div className="carousel-inner">
									<div className="carousel-item active">
										<div className="position-absolute top-50 start-50 translate-middle text-white">
											<div className="spinner-border" role="status"></div>
										</div>
										<div className="ratio ratio-16x9">
											<iframe
												src={url}
												title="YouTube video player"
												allow="accelerometer clipboard-write encrypted-media gyroscope picture-in-picture autoplay"
											></iframe>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</>
	);
};

export default Promo;
