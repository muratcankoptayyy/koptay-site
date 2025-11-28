import Meta from '@/components/Meta';
import React from 'react';
import Image from 'next/image';
import MenuList from '@/components/settings/menu-list';
import ChangeAvatarContainer from '@/container/settings/change-avatar/ChangeAvatarContainer';

function ChangeAvatar() {
	return (
		<div>
			<Meta title="Profil Fotoğrafını Değiştir"/>
			<div className="pt-[5.5rem] lg:pt-24">
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
				<Image
					width={613}
					height={415}
					src="https://cdn.tevkilapp.com/images/patterns/pattern_donut.png"
					alt="pattern donut"
					className="absolute right-0 top-0"
					style={{zIndex: -1}}
				/>

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

				<section className="relative py-16">
					<div className="container">
						<div className="flex flex-col gap-7">
							<div className="w-full">
								<MenuList/>
							</div>
							<div className="w-full">
								<div className="mb-3 pb-px mx-auto  lg:w-7/12">
									<h1 className="pt-3 mb-0 font-display text-xl font-medium text-jacarta-700 dark:text-white">
										Profil Fotoğrafı Güncelle
									</h1>
									<p className="dark:text-jacarta-100 font-medium text-2xs">
										Profil fotoğrafınızı yönetici onayı ile güncelleyebilirsiniz.
									</p>
								</div>
								<div className="flex lg:w-full items-center justify-center flex-wrap -mx-4">
									<div className="w-full lg:w-7/12 px-4 mb-8 lg:mb-0 ">
										<ChangeAvatarContainer/>
									</div>
								</div>
							</div>
						</div>
					</div>
				</section>
			</div>
		</div>
	);
}

export default ChangeAvatar;