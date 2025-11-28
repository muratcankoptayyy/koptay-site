import Link from 'next/link';
import {useEffect, useState} from 'react';

const CookieBanner = () => {

	const [isState, setShow] = useState(false);

	function acceptCookies() {
		document.cookie = 'acceptCookies=true; path=/';
		setShow(false);
	}

	useEffect(() => {
		// eğer kabul edilmiş bir çerez varsa bannerı gizle
		if (!document.cookie.includes('acceptCookies=true')) {
			setShow(false);
			// setShow(true);
		}
	}, []);

	return (
		<>
			{isState && (
				<div id="cookie-banner" className="fixed bottom-0 left-0 right-0 z-50 bg-blue-200 dark:bg-jacarta-800 dark:text-jacarta-300 p-4 shadow-2xl">
					<div className="container mx-auto flex flex-col lg:flex-row lg:items-center lg:justify-between gap-5 lg:gap-2">
						<div className="flex flex-row gap-4 text-blue-950 dark:text-jacarta-100">
							<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 32 32" className="w-10 h-10">
								<circle cx="10" cy="21" r="2" fill="currentColor"/>
								<circle cx="23" cy="20" r="2" fill="currentColor"/>
								<circle cx="13" cy="10" r="2" fill="currentColor"/>
								<circle cx="14" cy="15" r="1" fill="currentColor"/>
								<circle cx="23" cy="5" r="2" fill="currentColor"/>
								<circle cx="29" cy="3" r="1" fill="currentColor"/>
								<circle cx="16" cy="23" r="1" fill="currentColor"/>
								<path fill="currentColor" d="M16 30C8.3 30 2 23.7 2 16S8.3 2 16 2h.3l1.4.1l-.3 1.2c-.1.4-.2.9-.2 1.3c0 2.8 2.2 5 5 5c1 0 2-.3 2.9-.9l1.3 1.5c-.4.4-.6.9-.6 1.4c0 1.3 1.3 2.4 2.7 1.9l1.2-.5l.2 1.3c.1.6.1 1.2.1 1.7c0 7.7-6.3 14-14 14m-.7-26C9 4.4 4 9.6 4 16c0 6.6 5.4 12 12 12s12-5.4 12-12v-.4c-2.3.1-4.2-1.7-4.2-4v-.2c-.5.1-1 .2-1.6.2c-3.9 0-7-3.1-7-7c0-.2 0-.4.1-.6"/>
							</svg>
							<p className="text-sm">
								Sitemizin işleyişi için çerezler kullanılmaktadır.<br/>
								{' '}
								<Link href="/sayfa/cerez-politikasi" className="dark:text-accent text-blue-600 font-bold">
									Çerez Politikası
								</Link>
								{' '}
								sayfasından çerezler hakkında detayları öğrenebilirsiniz.
							</p>
						</div>

						<button className="btn bg-blue-600 dark:bg-indigo-700 rounded-full p-3 px-6 text-white" onClick={acceptCookies}>Tamam, Anladım!</button>
					</div>
				</div>
			)}
		</>
	);
};

export default CookieBanner;