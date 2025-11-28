import Image from "next/image";

const Story = ({ compFor }) => {
	if (compFor === "about") {
		return (
			<div>
				<section className="dark:bg-jacarta-800 relative py-24">
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
							<div className="lg:w-[55%]">
								<div className="relative">
									<Image
										width={515}
										height={515}
										src="https://cdn.tevkilapp.com/images/about-us-light.webp"
										alt="story"
										className="mx-auto mt-8 w-[80%] rotate-[8deg] rounded-[10rem]"
									/>
									<Image
										width={644}
										height={523}
										src="https://cdn.tevkilapp.com/images/hero/3D_elements.png"
										alt="3d"
										className="animate-fly absolute top-0 w-full h-full object-cover"
									/>
								</div>
							</div>

							{/* <!-- Info --> */}
							<div className="py-20 lg:w-[45%] lg:pl-16">
								<h2 className="text-jacarta-700 font-display mb-6 text-2xl dark:text-white">
									Uzman ekibimizle sizin için oluşturduk!
								</h2>
								<p className="dark:text-jacarta-300 mb-8 text-lg leading-normal">
									Yıllarca tevkil görevleri ile uğraşan ekibimiz, sizin için en iyi platformu oluşturmak için çalıştı. Siz de bu platformda yerinizi alın ve tevkil görevlerinizi kolayca oluşturun ve tevkil görevleri alın.
								</p>
								<p className="dark:text-jacarta-300 mb-10">
									Kısaca bahsedelim Tevkil, Avukatlar arası tevkil, bir avukatın ya da avukatlık bürosunun, bir davayı ya da hukuki bir işlemi diğer bir avukata ya da avukatlık bürosuna devretme işlemidir. Bu genellikle avukatın uzmanlık alanı veya iş yoğunluğu nedeniyle gerekebilir. Avukatlar arası tevkil, avukatların birbirlerine yardım etmelerini ve müvekkilleri için en iyi hizmeti sunmalarını sağlar. Bu işlem, avukatların etik kurallara ve yasal düzenlemelere uygun şekilde gerçekleştirilmelidir ve müvekkilin haklarını korumak amacıyla dikkatli bir şekilde yönetilmelidir.
								</p>
								<div className="flex flex-col sm:flex-row sm:space-x-10 gap-6">
									<div className="flex space-x-4">
										<svg
											xmlns="http://www.w3.org/2000/svg"
											viewBox="0 0 24 24"
											width="24"
											height="24"
											className="fill-accent h-8 w-8 shrink-0"
										>
											<path fill="none" d="M0 0h24v24H0z" />
											<path d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm0-2a8 8 0 1 0 0-16 8 8 0 0 0 0 16zm-.997-4L6.76 11.757l1.414-1.414 2.829 2.829 5.656-5.657 1.415 1.414L11.003 16z" />
										</svg>
										<div>
                      <span className="font-display text-jacarta-700 block text-xl dark:text-white">
                        11,2 bin+
                      </span>
											<span className="dark:text-jacarta-300 text-jacarta-700">
                        Tamamlanmış Tevkil
                      </span>
										</div>
									</div>
									<div className="flex space-x-4">
										<svg
											xmlns="http://www.w3.org/2000/svg"
											viewBox="0 0 24 24"
											width="24"
											height="24"
											className="fill-accent h-8 w-8 shrink-0"
										>
											<path fill="none" d="M0 0h24v24H0z" />
											<path d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm0-2a8 8 0 1 0 0-16 8 8 0 0 0 0 16zm-.997-4L6.76 11.757l1.414-1.414 2.829 2.829 5.656-5.657 1.415 1.414L11.003 16z" />
										</svg>
										<div>
                      <span className="font-display text-jacarta-700 block text-xl dark:text-white">
                        99,7%
                      </span>
											<span className="dark:text-jacarta-300 text-jacarta-700">
                       Başarı Oranı
                      </span>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</section>
			</div>
		);
	} else {
		return (
			<section className="dark:bg-jacarta-800 relative py-24">
				<picture className="pointer-events-none absolute inset-0 -z-10 dark:hidden">
					<Image
						width={1920}
						height={722}
						src="https://cdn.tevkilapp.com/images/gradient_light.jpg"
						alt="gradient"
						className="h-full w-full object-cover"
					/>
				</picture>
				<div className="container">
					<div className="lg:flex lg:items-center lg:justify-between">
						{/* <!-- Info --> */}
						<div className="pb-10 lg:w-[45%] lg:py-20 lg:pr-16">
							<h2 className="text-jacarta-700 font-display mb-6 text-2xl dark:text-white">
								Sign up for The Tide, {"Xhibiter's"} newsletter!
							</h2>
							<p className="dark:text-jacarta-300 mb-10 text-lg leading-normal">
								Join our mailing list to stay in the loop with our newest
								feature releases, NFT drops, and tips and tricks for navigating
								Xhibiter
							</p>

							<form className="relative">
								<input
									type="email"
									placeholder="Email address"
									className="dark:bg-jacarta-700 dark:border-jacarta-600 focus:ring-accent border-jacarta-100 w-full rounded-full border py-3 px-4 dark:text-white dark:placeholder-white"
								/>
								<button
									className="hover:bg-accent-dark font-display bg-accent absolute top-2 right-2 rounded-full px-6 py-2 text-sm text-white"
									onClick={(e) => e.preventDefault()}
								>
									Subscribe
								</button>
							</form>
						</div>

						{/* <!-- Image --> */}
						<div className="lg:w-[55%]">
							<div className="relative">
								<Image
									width={515}
									height={515}
									src="https://cdn.tevkilapp.com/images/about/story.jpg"
									alt="story"
									className="mx-auto mt-8 w-[80%] rotate-[8deg] rounded-[10rem]"
								/>
								<Image
									width={644}
									height={523}
									src="https://cdn.tevkilapp.com/images/hero/3D_elements.png"
									alt="3d"
									className="animate-fly absolute top-0 w-full h-full object-cover"
								/>
							</div>
						</div>
					</div>
				</div>
			</section>
		);
	}
};

export default Story;