/* eslint-disable react/no-unescaped-entities */
import React, { useState, useEffect } from 'react';

const texts = [
	{
		title: "İşlerinizi Kolaylaştırın!",
		description: "Vaktinizi boşa harcamayın! TevkilApp, tevkil platformu sayesinde işlerinizi kolaylaştıracak meslektaşlarınıza ulaşın."
	},
	{
		title: "Hızlı ve Güvenilir Tevkil!",
		description: "Türkiye'nin her yerinden meslektaşlarınızla güvenli bir şekilde iletişime geçin."
	},
	{
		title: "Profesyonel Çözümler!",
		description: "Tevkil işlemlerinizi dijital ortamda profesyonelce yönetin."
	}
];

const SlideText = ({ text }) => {
	const [isVisible, setIsVisible] = useState(true);

	return (
		<div className={`transition-all duration-500 transform ${isVisible ? 'translate-x-0 opacity-100' : '-translate-x-full opacity-0'}`}>
			{text}
		</div>
	);
};

const Services = () => {
	const [currentTextIndex, setCurrentTextIndex] = useState(0);
	const [isVisible, setIsVisible] = useState(true);

	useEffect(() => {
		const interval = setInterval(() => {
			// Önce metni gizle
			setIsVisible(false);
			
			// 500ms sonra yeni metne geç ve göster
			setTimeout(() => {
				setCurrentTextIndex((prevIndex) => (prevIndex + 1) % texts.length);
				setIsVisible(true);
			}, 500);
			
		}, 5000);

		return () => clearInterval(interval);
	}, []);

	return (
		<div>
			<section className="py-12 dark:bg-jacarta-900">
				<div className="container">
					<div className="mx-auto mb-12 max-w-xl text-center overflow-hidden">
						<h2 className="mb-6 text-center font-display text-3xl font-medium text-jacarta-700 dark:text-white h-12">
							<div className={`transition-all duration-500 transform ${isVisible ? 'translate-x-0 opacity-100' : '-translate-x-full opacity-0'}`}>
								{texts[currentTextIndex].title}
							</div>
						</h2>
						<p className="text-lg dark:text-jacarta-300 block h-24">
							<div className={`transition-all duration-500 transform ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}`}>
								{texts[currentTextIndex].description}
							</div>
						</p>
					</div>
				</div>
			</section>
		</div>
	);
};

export default Services;
