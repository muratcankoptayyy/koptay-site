import Image from 'next/image';

export const BenefitImage = ({src, alt}) => {
	return (
		<div className=" relative">
			<figure className="flex items-center justify-center">
				<Image
					width={526}
					height={526}
					src={src}
					alt={alt}
					className="rounded-full border border-jacarta-100 p-14 dark:border-jacarta-600  object-contain"
				/>
				<Image
					width={630}
					height={594}
					src="https://cdn.tevkilapp.com/images/dao/3d_elements_circle.png"
					alt="circle"
					className="absolute animate-spin-slow"
					priority
				/>
			</figure>
		</div>
	);
};