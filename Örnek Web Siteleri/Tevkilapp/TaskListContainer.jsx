import Sidebar from '@/components/collections-wide/sidebar';
import React from 'react';
import TaskListTable from '@/container/tasks/list/TaskListTable';

const TaskListContainer = ({data}) => {
	const [taskData, setTaskData] = React.useState(data);
	return (
		<div className="lg:flex mt-6">
			{/* Sidebar */}
			<Sidebar setData={setTaskData}/>
			{/* end sidebar */}
			{/* Content */}
			<TaskListTable taskData={taskData}/>
			{/* end content */}
		</div>
	);
};

export default TaskListContainer;