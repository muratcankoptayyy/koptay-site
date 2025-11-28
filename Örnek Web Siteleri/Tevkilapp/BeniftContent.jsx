import {Tab, Tabs, TabList, TabPanel} from 'react-tabs';
import {BenefitImage} from '@/components/benefit/BenefitImage';

const images = [
	{
		src: 'https://cdn.tevkilapp.com/images/uploads/tevkilapp-banner-sira-2.png',
		alt: 'benifit',
	},
	{
		src: 'https://cdn.tevkilapp.com/images/uploads/tevkilapp-uyusmazlik-masasi.png',
		alt: 'benifit',
	},
	{
		src: 'https://cdn.tevkilapp.com/images/uploads/tevkilapp-referans.png',
		alt: 'benifit',
	},
	{
		src: 'https://cdn.tevkilapp.com/images/uploads/tevkilapp-uyusmazlik-masasi.png',
		alt: 'benifit',
	},
	{
		src: 'https://cdn.tevkilapp.com/images/uploads/tevkilapp-multi-platform.png',
		alt: 'benifit',
	},
];

const BeniftContent = () => {
	return (
		<Tabs>
			<div className="flex flex-col sm:flex-row lg:flex-nowrap lg:space-x-10 benifit">
				<div className="lg:w-[43%]">
					{/* <!-- tabs --> */}

					<TabList className="nav nav-tabs mb-12 space-y-2">
						<Tab className="nav-item">
							<button
								className="nav-link nav-link--style-2  group relative flex w-full border-jacarta-100 p-6 text-left dark:border-jacarta-600 dark:bg-transpare"
								type="button"
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 24 24"
									width="24"
									height="24"
									className="mr-2 h-8 w-8 flex-shrink-0 fill-accent"
								>
									<path fill="none" d="M0 0h24v24H0z"/>
									<path d="M17 15.245v6.872a.5.5 0 0 1-.757.429L12 20l-4.243 2.546a.5.5 0 0 1-.757-.43v-6.87a8 8 0 1 1 10 0zM12 15a6 6 0 1 0 0-12 6 6 0 0 0 0 12zm0-2a4 4 0 1 1 0-8 4 4 0 0 1 0 8z"/>
								</svg>

								<div>
                  <span className="mb-2 mt-1 block font-display text-xl font-medium group-hover:text-accent dark:text-white transition transition-colors">
                    CMK Benzeri Sıra Sistemi
                  </span>
									<div className="nav-link-content hidden">
										<p className="text-jacarta-500 dark:text-jacarta-300">
											CMK benzeri sıra sistemi ile adil ve düzenli olarak görev kaçırma riski olmadan tevkil görevi alın, gelir elde edin.
										</p>
									</div>
								</div>
							</button>
						</Tab>
						{/* End tab */}

						<Tab className="nav-item">
							<button
								className="nav-link nav-link--style-2 group relative flex w-full border-b border-jacarta-100 p-6 text-left dark:border-jacarta-600"
								type="button"
							>
								<svg width="24" height="24" className="mr-2 h-8 w-8 flex-shrink-0 fill-accent" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
									<path d="M9 2a4 4 0 1 0 0 8 4 4 0 0 0 0-8Zm-4.991 9A2.001 2.001 0 0 0 2 13c0 1.691.833 2.966 2.135 3.797C5.417 17.614 7.145 18 9 18c.41 0 .816-.019 1.21-.057A5.477 5.477 0 0 1 9 14.5c0-1.33.472-2.55 1.257-3.5H4.01Zm9.866 1.5a.625.625 0 1 1 1.25 0 .625.625 0 0 1-1.25 0Zm1.125 4a.5.5 0 0 1-1 0v-2a.5.5 0 0 1 1 0v2Zm-5-2a4.5 4.5 0 1 1 9 0 4.5 4.5 0 0 1-9 0Zm1 0a3.5 3.5 0 1 0 7 0 3.5 3.5 0 0 0-7 0Z"></path>
								</svg>

								<div>
                  <span className="mb-2 mt-1 block font-display text-xl font-medium text-jacarta-700 group-hover:text-accent dark:text-white transition transition-colors">
                    Bilgilendirme ve Mazeret Sistemi
                  </span>
									<div className="nav-link-content hidden">
										<p className="text-jacarta-500 dark:text-jacarta-300">
											Aktif bulunduğunuz bölgede tevkil görevi verildiğinde; sıralamada ilk onda iseniz SMS ile bilgilendirileceksiniz. Görevi TevkilApp&apos;e girerek kabul edebilirsiniz. Görevlendirmelere gitmek için uygun olmadığınız zamanlarda sıranızı durdurup sıra kaçırma riski olmadan daha sonra kaldığınız sıradan devam edebilirsiniz.
										</p>
									</div>
								</div>
							</button>
						</Tab>

						<Tab className="nav-item">
							<button
								className="nav-link nav-link--style-2 group relative flex w-full border-b border-jacarta-100 p-6 text-left dark:border-jacarta-600"
								type="button"
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 24 24"
									width="24"
									height="24"
									className="mr-2 h-8 w-8 flex-shrink-0 fill-accent"
								>
									<path fill="none" d="M0 0h24v24H0z"/>
									<path d="M21 2.992v18.016a1 1 0 0 1-.993.992H3.993A.993.993 0 0 1 3 21.008V2.992A1 1 0 0 1 3.993 2h16.014c.548 0 .993.444.993.992zm-9.707 10.13l-2.475-2.476-1.414 1.415 3.889 3.889 5.657-5.657-1.414-1.414-4.243 4.242z"/>
								</svg>

								<div>
                  <span className="mb-2 mt-1 block font-display text-xl font-medium text-jacarta-700 group-hover:text-accent dark:text-white transition transition-colors">
                    Referans Sistemi
                  </span>
									<div className="nav-link-content hidden">
										<p className="text-jacarta-500 dark:text-jacarta-300">
											Referans sistem ile davet ettiğiniz kullanıcı başına gelir elde edebilirsiniz.
										</p>
									</div>
								</div>
							</button>
						</Tab>
						{/* End tab */}

						<Tab className="nav-item">
							<button
								className="nav-link nav-link--style-2 group relative flex w-full border-b border-jacarta-100 p-6 text-left dark:border-jacarta-600"
								type="button"
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 24 24"
									width="24"
									height="24"
									className="mr-2 h-8 w-8 flex-shrink-0 fill-accent"
								>
									<path fill="none" d="M0 0h24v24H0z"/>
									<path d="M12 2c5.523 0 10 4.477 10 10s-4.477 10-10 10a9.96 9.96 0 0 1-6.383-2.302l-.244-.209.902-1.902a8 8 0 1 0-2.27-5.837l-.005.25h2.5l-2.706 5.716A9.954 9.954 0 0 1 2 12C2 6.477 6.477 2 12 2zm1 4v2h2.5v2H10a.5.5 0 0 0-.09.992L10 11h4a2.5 2.5 0 1 1 0 5h-1v2h-2v-2H8.5v-2H14a.5.5 0 0 0 .09-.992L14 13h-4a2.5 2.5 0 1 1 0-5h1V6h2z"/>
								</svg>

								<div>
                  <span className="mb-2 mt-1 block font-display text-xl font-medium text-jacarta-700 group-hover:text-accent dark:text-white transition transition-colors">
                    Destek Masası
                  </span>
									<div className="nav-link-content hidden">
										<p className="text-jacarta-500 dark:text-jacarta-300">
											Tevkil işlemlerinizde bir sorun yaşandığında yapay zeka destekli destek masası ile sorunlarınızı hızlıca çözüme kavuşturabilirsiniz.
										</p>
									</div>
								</div>
							</button>
						</Tab>
						{/* End tab */}

						<Tab className="nav-item">
							<button
								className="nav-link nav-link--style-2 group relative flex w-full border-b border-jacarta-100 p-6 text-left dark:border-jacarta-600"
								type="button"
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 24 24"
									width="24"
									height="24"
									className="mr-2 h-8 w-8 flex-shrink-0 fill-accent"
								>
									<path fill="none" d="M0 0h24v24H0z"/>
									<path d="M6.75 2.5A4.25 4.25 0 0 1 11 6.75V11H6.75a4.25 4.25 0 1 1 0-8.5zm0 10.5H11v4.25A4.25 4.25 0 1 1 6.75 13zm10.5-10.5a4.25 4.25 0 1 1 0 8.5H13V6.75a4.25 4.25 0 0 1 4.25-4.25zM13 13h4.25A4.25 4.25 0 1 1 13 17.25V13z"/>
								</svg>

								<div>
                  <span className="mb-2 mt-1 block font-display text-xl font-medium text-jacarta-700 group-hover:text-accent dark:text-white transition transition-colors">
                    Çoklu Platform
                  </span>
									<div className="nav-link-content hidden">
										<p className="text-jacarta-500 dark:text-jacarta-300">
											Yeni teknoloji ile geliştirilmiş TevkilApp platformuna tüm cihazlardan kolay ve güvenilir bir şekilde ulaşabilir, işlemlerinizi halledebilirsiniz.
										</p>
									</div>
								</div>
							</button>
						</Tab>

					</TabList>
				</div>
				{/* End tablist */}

				<div className="flex items-center justify-center lg:w-[57%] mb-10 sm:mb-0">
					{/* <!-- content --> */}
					<div className="tab-content flex-1">
						{images.map((image, index) => (
							<TabPanel key={index}>
								<BenefitImage src={image.src} alt={image.alt}/>
							</TabPanel>
						))}

					</div>
				</div>
			</div>
		</Tabs>
	);
};

export default BeniftContent;
