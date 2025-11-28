import {Tab, TabPanel, Tabs, TabsBody, TabsHeader} from '@material-tailwind/react';
import TableComponent from '@/components/TableComponent';
import React, {useCallback} from 'react';
import request from '@/utils/request';
import MyTaskDropdown from '@/components/dropdown/myTaskDropdown';

export const TabContainer = ({activeTask}) => {
	const [taskList, setTaskList] = React.useState(activeTask);
	const [loading, setLoading] = React.useState(false);
	const [anyDropdownIsOpen, setAnyDropdownIsOpen] = React.useState({
		id: 0,
		open: false,
	});
	const tableColumns = [
		{
			id: 'id',
			name: 'Görev No',
			width: 'w-1/12',
		},
		{
			id: 'titleName',
			name: 'Görev Başlığı',
			width: 'w-2/12',
		},
		{
			id: 'content',
			name: 'Görev İçeriği',
			width: 'w-4/12',
		},
		{
			id: 'taskLocation',
			name: 'Görev Yeri',
			width: 'w-2/12',
			render: (item) => {
				return <>
					{item.courthouse_id !== 0 ? (
						<>{item.courtHouse}</>
					) : (
						<>{item.city.name} / {item.district.name}</>
					)}
				</>;
			},
		},
		{
			id: 'datetime',
			name: 'Oluşturulma Tarihi',
			width: 'w-2/12',
		},
		{
			id: 'action',
			name: 'İşlem',
			width: 'w-1/12',
			render: (item) => {
				return <MyTaskDropdown anyDropdownIsOpen={anyDropdownIsOpen} setAnyDropdownIsOpen={setAnyDropdownIsOpen} taskList={taskList} setTaskList={setTaskList} data={item} classes="dark:border-jacarta-600 dark:hover:bg-jacarta-600 border-jacarta-100 dropdown hover:bg-jacarta-100 dark:bg-jacarta-700 rounded-xl border bg-white "/>;
			},
		},
	];
	const [activeTab, setActiveTab] = React.useState('active');
	const handleGetMyTask = async (url) => {
		if (url === activeTab) {
			return;
		}
		setActiveTab(url);
		setLoading(true);
		const {data, success} = await request(`/task/me/${url}`, 'GET', null, true, false, true, 250);
		if (success) {
			setTaskList(data);
		}
		setLoading(false);
	};

	return (
		<div className="container">
			<div className="mb-8 pb-px">
				<h1 className="pt-3 mb-0 font-display text-2xl font-medium text-jacarta-700 dark:text-white">
					Görevlerim
				</h1>
				<p className="dark:text-jacarta-100 font-medium text-2xs">
					Oluşturmuş olduğunuz aktif ve geçmiş görevleriniz burada listelenmektedir.
				</p>
			</div>

			<Tabs className="z-0" value="aktif-gorevlerim" id="my-tasks">
				<TabsHeader className="bg-white dark:bg-jacarta-800 z-0 rounded-lg shadow-lg border border-gray-200 dark:border-jacarta-600">
					<Tab 
						onClick={() => handleGetMyTask('active')} 
						key="my-tasks-active" 
						value="aktif-gorevlerim" 
						className="px-6 py-3 text-sm font-medium transition-all duration-300 hover:bg-gray-50 dark:hover:bg-jacarta-700 rounded-lg"
					>
						Aktif Görevlerim
					</Tab>
					<Tab 
						onClick={() => handleGetMyTask('inactive')} 
						key="my-tasks-inactive" 
						value="gecmis-gorevlerim" 
						className="px-6 py-3 text-sm font-medium transition-all duration-300 hover:bg-gray-50 dark:hover:bg-jacarta-700 rounded-lg"
					>
						Geçmiş Görevlerim
					</Tab>
				</TabsHeader>
				<TabsBody className="mt-6 rounded-lg shadow-lg border border-gray-200 dark:border-jacarta-600 bg-white dark:bg-jacarta-800" style={{paddingBottom: '130px'}}>
					<TabPanel className=" fade show active" key="my-tasks-active" value="aktif-gorevlerim" style={{padding: '0px'}}>

						<TableComponent emptyTitle="Aktif Göreviniz Bulunmamaktadır." emptyContent="Geçmiş görevlerinizi görmek için geçmiş görevlerim sekmesine tıklayınız." loading={loading} columns={tableColumns} data={taskList}/>

					</TabPanel>
					<TabPanel className="p-0" key="my-tasks-inactive" value="gecmis-gorevlerim">

						<TableComponent emptyTitle="Geçmiş Göreviniz Bulunmamaktadır" emptyContent="Aktif görevlerinizi görmek için aktif görevlerim sekmesine tıklayınız." loading={loading} columns={tableColumns} data={taskList}/>


					</TabPanel>
				</TabsBody>
			</Tabs>
		</div>
	);
};