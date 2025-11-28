import moment from 'moment/moment';
import React from 'react';

export const TableData = ({data, columns, dateFormat}) => {
	//
	// 0 = Görev Bekliyor
	// 1 = Talep Topluyor
	// 2 = Görev İşlemde
	// 3 = Görev İptal Edildi
	// 4 = Görev Tamamlandı
	const handleStatus = (status) => {
		switch (status) {
			case 0:
				return {
					color: 'bg-yellow-700', text: 'Görev Bekliyor',
				};
			case 1:
				return {
					color: 'bg-blue', text: 'Talep Topluyor',
				};
			case 2:
				return {
					color: 'bg-cyan-500', text: 'Görev İşlemde',
				};
			case 3:
				return {
					color: 'bg-red-500', text: 'Görev İptal Edildi',
				};
			case 4:
				return {
					color: 'bg-green', text: 'Görev Tamamlandı',
				};
			default:
				return {
					color: 'bg-yellow-700', text: 'Görev Bekliyor',
				};
		}
	};

	const handleDateFormat = (date) => {
		const today = new Date();
		const dateToCompare = new Date(date);
		const diffTime = dateToCompare - today;
		const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
		const diffHours = Math.round(diffTime / (1000 * 60 * 60));
		const diffMinutes = Math.round(diffTime / (1000 * 60));
		const diffSeconds = Math.round(diffTime / (1000));
		if (diffDays < 0 || diffHours < 0 || diffMinutes < 0 || diffSeconds < 0) {
			return `${Math.abs(diffDays)} gün önce`;
		}
		if (diffDays > 0) {
			return `${diffDays} gün sonra`;
		}
		else {
			if (diffHours > 0) {
				return `${diffHours} saat sonra`;
			}
			else {
				if (diffMinutes > 0) {
					return `${diffMinutes} dakika sonra`;
				}
				else {
					if (diffSeconds > 0) {
						return `${diffSeconds} saniye sonra`;
					}
				}
			}
		}
	};

	return (
		<>
			{data.map((item, index) => (

				<tr key={index} className="hover:bg-gray-100 hover:dark:bg-gray-800 cursor-pointer">
					{columns.map((column, key) => (
						<td
							key={key + item.id}
							className={`${column.width} px-6 py-4 ${column.position ? column.position : 'text-center'} whitespace-nowrap text-sm text-gray-500 dark:text-gray-300 relative`}
						>
							{column.id === 'action' ? (
								<>
									{column.render(item)}
								</>) : (<>
								{typeof item[column.id] === 'string' ? (<>
									{column.id === 'datetime' || column.id === 'created_at' ? (<>
										{dateFormat ? (<>
											{handleDateFormat(item[column.id])}
										</>) : (<>
											{moment.utc(item[column.id]).local().format('DD.MM.YYYY')}
										</>)}
									</>) : (<>
										{column.id === 'price' ? (
											<>
												<p className="text-sm font-black">{item[column.id].split('.')[0]},<span className="text-xs font-normal">{item[column.id].split('.')[1]}</span> ₺</p>
											</>
										) : (
											<>
												{column.id === 'task_paired_user' ? (
													<>
													<span
														className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${handleStatus(item['pair_state']).color} text-white`}
													>
																					{item[column.id]}
																				</span>
													</>
												) : (
													item[column.id].length > 50 ? item[column.id].substring(0, 50) + '...' : item[column.id]
												)}
											</>
										)}
									</>)}
								</>) : (<>
									{column.id === 'state' || column.id === 'task_paired_user' ? (<>
																				<span
																					className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${handleStatus(item[column.id]).color} text-white`}
																				>
																					{handleStatus(item[column.id]).text}
																				</span>
									</>) : (<>
										{column.id === 'confirm_at' ? (
											<>
												{item[column.id] !== null ? moment.utc(item[column.id]).local().format('DD.MM.YYYY') : (
													<>
														<p className="text-red-400">Onaylanmadı</p>
													</>
												)}
											</>
										) : (
											<>
												{column.id === 'taskLocation' ? (
													<>{column.render(item)}</>
												) : (
													<>
														{item[column.id]}
													</>
												)}
											</>
										)}

									</>)}

								</>)}
							</>)}
						</td>))}
				</tr>

			))}
		</>
	);
};