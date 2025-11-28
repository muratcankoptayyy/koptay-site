import {BsFillInboxFill} from 'react-icons/bs';
import {AiOutlineLoading} from 'react-icons/ai';
import React from 'react';
import {TableData} from '@/container/tasks/list/TableData';

function TableComponent({columns, data, loading, emptyTitle, emptyContent, dateFormat}) {

	return (
		<div className="flex flex-col">
			<div className="sm:-mx-6 lg:-mx-8">
				<div className=" align-middle inline-block min-w-full w-full sm:px-6 lg:px-8">
					<div className="shadow border border-gray-200 dark:border-gray-800 rounded-lg p-1 bg-white dark:bg-jacarta-800 w-full overflow-x-auto">
						{!loading ? (

							<>
								{data.length > 0 ? (
									<table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 rounded-lg ">
										<thead className="bg-gray-50 dark:bg-gray-800">
										<tr>
											{columns.map((column, key) => (
												<th
													key={key}
													scope="col"
													className={`${column.width} px-6 py-3 ${column.position ? column.position : 'text-center'} text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider`}
												>
													{column.name}
												</th>))}
										</tr>
										</thead>
										<tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
										<TableData dateFormat={dateFormat} data={data} columns={columns}/>
										</tbody>
									</table>) : (<div className="flex flex-col items-center justify-center my-7">
									<BsFillInboxFill className="text-6xl mb-4"></BsFillInboxFill>
									<div className="text-gray-600 dark:text-jacarta-100 w-100">{emptyTitle}</div>
									<div className="text-gray-400 dark:text-jacarta-400 text-sm">{emptyContent}</div>
								</div>)}
							</>

						) : (<div className="flex flex-col items-center justify-center my-9">
							<AiOutlineLoading className="text-5xl mb-6 animate-spin"></AiOutlineLoading>
							<div className="text-gray-600 dark:text-jacarta-100">Veriler yükleniyor lütfen bekleyiniz.</div>
							<div className="text-gray-400 dark:text-jacarta-400 text-sm">Lütfen sayfayı yenilemeyiniz.</div>
						</div>)}
					</div>
				</div>
			</div>
		</div>);
}

export default TableComponent;