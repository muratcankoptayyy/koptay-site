import React from 'react';
import Meta from '@/components/Meta';
import serverRequest from '@/utils/serverRequest';
import {TabContainer} from '@/container/tasks/my-tasks/TabContainer';
import {PictureComponent} from '@/components/picture/PictureComponent';

export async function getServerSideProps(context) {
	const userToken = context.req.cookies.userToken;
	const getActiveMyTask = await serverRequest('/task/me/active', 'GET', null, userToken, null);

	return {
		props: {
			activeTask: getActiveMyTask.data,
		},
	};
}

function MyTasks({activeTask}) {

	return (
		<>
			<Meta title="Görevlerim"/>
			<section className="relative pt-24 lg:pb-96 pb-0">
				<PictureComponent/>

				<div className="py-16  md:py-24">
					<TabContainer activeTask={activeTask}/>
				</div>
			</section>
		</>
	);
}

export default MyTasks;