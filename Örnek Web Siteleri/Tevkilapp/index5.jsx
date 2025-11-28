import Image from 'next/image';
import Meta from '@/components/Meta';
import React from 'react';
import serverRequest from '@/utils/serverRequest';
import TaskListContainer from '@/container/tasks/list/TaskListContainer';

export const getServerSideProps = async (context) => {
		const userToken = context.req.cookies.userToken;
		const {data, success} = await serverRequest(`/task/available`, 'GET', null, userToken);
		if (success) {

			data.map((item) => {
				item.price = `${item.price} ₺`;
			});
			return {
				props: {
					data,
				},
			};
		}
		return {
			props: {
				data,
			},
		};
	}
;

function TaskList({data}) {

	return (
		<>
			<Meta title="Görev Listesi"/>
			{/* End page title */}

			<main className="">
				{/* Collections */}
				<section className="relative pt-16 pb-24">
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
					<div className="px-6 xl:px-24">

						<TaskListContainer data={data}/>
					</div>
				</section>
				{/* end collections */}
			</main>
		</>
	);
};

export default TaskList;
