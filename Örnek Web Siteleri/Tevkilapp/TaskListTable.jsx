import TableComponent from '@/components/TableComponent';
import React from 'react';
import Link from 'next/link';
import LoaderComponent from '@/components/LoaderComponent';

const columns = [
	{
		id: 'id',
		name: 'Görev No',
		width: 'w-1/12',
	},
	{
		id: 'titleName',
		name: 'Görev Başlığı',
		width: 'w-3/12',
	},
	{
		id: 'datetime',
		name: 'Görev Tarihi',
		width: 'w-2/12',
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
		id: 'price',
		name: 'Görev Ücreti',
		width: 'w-2/12',
	},
	{
		id: 'state',
		name: 'Durum',
		width: 'w-2/12',
	},
	{
		id: 'action',
		name: 'İşlemler',
		width: 'w-1/12',
		render: (item) => {
			return <>
				<Link prefetch={false} href={`/gorevler/detay/${item.id}`} className="text-jacarta-500 hover:text-jacarta-700 dark:text-white dark:hover:text-white">
					<button
						className="bg-accent shadow-accent-volume hover:bg-accent-hover text-white font-bold py-3 px-8 rounded-xl w-full transition-colors"
					>
						Görevi Görüntüle
					</button>
				</Link>
			</>;

		},
	},
];

const TaskListTable = ({taskData}) => {
	return (
		<div className="lg:w-full js-collections-content">
			<div className="mb-8 pb-px">
				<h1 className="pt-3 mb-2 font-display text-2xl font-medium text-jacarta-700 dark:text-white">
					Görev Listesi
				</h1>
				<p className="dark:text-jacarta-400 font-medium text-2xs">
					Şu anda size uygun {taskData.length} adet görev bulunmaktadır.
				</p>
			</div>
			<TableComponent clickable dateFormat={true} data={taskData} columns={columns} emptyTitle="Şu anda hiç görev bulunmamaktadır." emptyContent="Sizin kriterlerinize uygun görevler eklendiğinde sizi bilgilendireceğiz."/>
		</div>
	);
};

export default TaskListTable;