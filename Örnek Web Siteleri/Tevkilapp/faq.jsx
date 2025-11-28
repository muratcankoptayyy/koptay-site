import Image from 'next/image';
import FaqAccordion from './accoedion';
import Link from 'next/link';

const Faq = () => {
	return (
		<div>
			{/* <!-- FAQ --> */}
			<section className="relative py-24 dark:bg-jacarta-800">
				<div className="container">
					<div className="justify-between lg:flex lg:space-x-20">
						<div className="lg:w-[45%]">
							<h2 className="mb-6 font-display text-3xl font-medium text-jacarta-700 dark:text-white">
								Sıkça Sorulan Sorular
							</h2>
							<p className="mb-12 text-lg dark:text-jacarta-300">
								TevkilApp platformu ile alakalı en çok sorulan soruları buradan görüntüleyebilirsiniz, sorularınızın cevabını bulamadıysanız bizimle iletişime geçebilirsiniz.
							</p>

							<FaqAccordion/>


							<Link
								href="/sss"
								className="rounded-full bg-accent py-3 px-8 -mt-4 text-center sm:w-fit w-full font-semibold text-white shadow-accent-volume transition-all hover:bg-accent-dark"
							>
								Diğer Sıkça Sorulan Sorular
							</Link>

							<p className="text-lg text-jacarta-700 mt-6 dark:text-jacarta-100">
								Aklınıza bir şey mi takıldı?
								<br/>
								<a href="#" className="text-accent">
									destek@tevkilapp.com
								</a>
							</p>
						</div>
						<div className="lg:w-[55%]">
							<div className="mt-12 md:flex md:space-x-8 lg:justify-end">
								<div className="relative mb-8 max-w-[13.125rem] self-end rounded-2.5xl bg-green p-8 shadow-2xl">
									<Image
										width={60}
										height={60}
										src="https://cdn.tevkilapp.com/images/patterns/pattern_circle_1.png"
										className="absolute -top-10 -left-8 -z-10 animate-fly dark:z-0 dark:opacity-10"
										alt="pattern"
									/>
									<div>
                    <span className="mb-4 block font-display text-base text-white">
                      Başarılı Görevlendirme
                    </span>
										<span className="mb-4 block font-display text-4xl text-white">
                     +5000
                    </span>
									</div>
								</div>
								<Image
									width={320}
									height={320}
									src="https://cdn.tevkilapp.com/images/tevkilapp-home-sss.png"
									className="mb-8 inline-block rounded-2.5xl"
									alt="faq"
								/>
							</div>
							<div className="relative">
								<Image
									width={150}
									height={150}
									src="https://cdn.tevkilapp.com/images/patterns/pattern_circle_2.png"
									className="absolute -bottom-8 right-12 animate-fly dark:opacity-10"
									alt="pattern"
								/>
								<div className="relative mx-auto max-w-xs self-start rounded-2.5xl bg-blue p-8 shadow-2xl">
									<div className="text-left">
                    <span className="mb-4 block font-display text-base text-white">
                      TevkilApp
                    </span>
										<span className="mb-4 block font-display text-4xl text-white">
                     81 İl
                    </span>
										<span className="block text-base text-white">
                      Tevkilapp, 81 ildeki 922 ilçedeki tüm adliyelerde!
                    </span>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</section>
			{/* <!-- end faq --> */}
		</div>
	);
};

export default Faq;
