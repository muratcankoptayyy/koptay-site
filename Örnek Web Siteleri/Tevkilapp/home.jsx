import React from 'react';
import Meta from '@/components/Meta';
import Hero_7 from '@/components/hero/hero_7';
import Services from '@/components/services/services';
import Promo from '@/components/promo/promo';
import Faq from '@/components/faq/faq';
import Financialnews from '@/components/blog/financialnews';
import DownloadAppBanner from '@/components/DownloadAppBanner';

const Home = () => {
	return (
		<>
			<Meta title="Anasayfa"/>
			<Hero_7/>
			<Services/>
			<Promo/>
			<Faq/>
			<Financialnews/>
			<DownloadAppBanner/>
		</>
	);
};

export default Home;
