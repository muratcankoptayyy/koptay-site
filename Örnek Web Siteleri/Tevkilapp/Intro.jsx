import Image from 'next/image';
import {useTheme} from 'next-themes';

const Intro = ({data}) => {
	const {theme, setTheme} = useTheme();

	return (
		// <!-- Intro -->
		<section className="sm:bg-gradient-to-r sm:from-[transparent_33%] sm:to-[#F5F8FA_33%] py-36 sm:dark:to-[#101436_33%]">
			<div className="container">
				<div className="lg:flex lg:justify-between">
					{/* <!-- Image --> */}
					<div className="relative lg:w-[45%]">
						<figure className="relative">
							{
								(theme === 'dark') ? (
									<Image
										width={500}
										height={500}
										src="https://cdn.tevkilapp.com/images/tevkilapp-dark-how-to-work.png"
										className="rounded-2.5xl w-full h-full object-cover"
										alt="web protocol"
									/>
								) : (
									<Image
										width={500}
										height={500}
										src="https://cdn.tevkilapp.com/images/tevkilapp-how-to-work.png"
										className="rounded-2.5xl w-full h-full object-cover"
										alt="web protocol"
										priority
									/>
								)
							}
						</figure>
					</div>

					{/* <!-- Info --> */}
					{data.content && (
						<div className="py-10 lg:w-[55%] lg:pl-24">
							<h2 className="mb-6 font-display text-3xl text-jacarta-700 dark:text-white">
								{data.title}
							</h2>
							<p className="mb-8 text-lg leading-normal dark:text-jacarta-300 page-content-area" dangerouslySetInnerHTML={{__html: data.content}}></p>
						</div>
					)}
				</div>
			</div>
		</section>
		// <!-- end intro -->
	);
};

export default Intro;
