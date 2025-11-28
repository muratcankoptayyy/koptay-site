import Image from 'next/image';
import React from 'react';

export const PictureComponent = () => {
	return (
		<>
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
		</>
	);
};