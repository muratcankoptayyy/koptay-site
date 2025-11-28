import Image from 'next/image';
import React, {useEffect} from 'react';
import request from '../../../../utils/request';

const CollectionsItem = ({handleGetFilterTask, searchTerm}) => {
	const [getTaskTitles, setTaskTitles] = React.useState([]);
	const [filteredTaskTitles, setFilteredTaskTitles] = React.useState([]);

	const handleSendFilter = (checked, id) => {
		if (checked) {
			handleGetFilterTask(id, 'title', true);
		}
		else {
			handleGetFilterTask(id, 'title', false);
		}
	};

	React.useEffect(() => {
		const getTaskTitles = async () => {
			const response = await request('/task/title', 'POST', false, true, null, true, 500);
			setTaskTitles(response.data);
			setFilteredTaskTitles(response.data);
		};

		getTaskTitles();
	}, []);

	useEffect(() => {
		if (searchTerm) {
			const results = getTaskTitles.filter((taskTitle) =>
				taskTitle.name.toLowerCase().includes(searchTerm.toLowerCase()),
			);
			setFilteredTaskTitles(results);
		}
		else {
			setFilteredTaskTitles(getTaskTitles);
		}
	}, [getTaskTitles, searchTerm]);

	return (
		<>
			{filteredTaskTitles.map((item) => (
				<li key={item.id}>
					<label className="flex items-center cursor-pointer w-full">
						<input
							type="checkbox"
							id={item.id}
							onChange={(e) => {
								handleSendFilter(e.target.checked, item.id);
							}}
							className="h-5 w-5 mr-3 rounded border-jacarta-200 text-accent checked:bg-accent focus:ring-accent/20 focus:ring-offset-0 dark:border-jacarta-500 dark:bg-jacarta-600"
						/>
						<span className="font-display text-sm font-semibold text-jacarta-700 dark:text-white">
						  {item.name}
						</span>
					</label>
				</li>
			))}
		</>
	);
};

export default CollectionsItem;
