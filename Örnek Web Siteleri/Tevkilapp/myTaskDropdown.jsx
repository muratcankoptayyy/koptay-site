import React, {useEffect, useState} from 'react';
import Link from 'next/link';
import {BiExit, BiPencil, BiShow} from 'react-icons/bi';
import request from '../../utils/request';
import Swal from 'sweetalert2';
import {FiUsers} from 'react-icons/fi';

const MyTaskDropdown = ({classes, data, setTaskList, taskList, anyDropdownIsOpen, setAnyDropdownIsOpen}) => {
		const [dropdownShow, setDropdownShow] = useState(false);
		const handleCancelTask = async () => {
			await Swal.fire({
				title: 'Görevi iptal etmek istediğinize emin misiniz?',
				text: 'Bu işlem geri alınamaz!',
				icon: 'warning',
				showCancelButton: true,
				confirmButtonText: 'Evet',
				cancelButtonText: 'Hayır',
				reverseButtons: true,
			}).then(async (result) => {
				if (result.isConfirmed) {
					const response = await request(`/task/${data.id}/cancel`, 'GET', null, true);
					if (response.success) {
						await Swal.fire({
							title: 'Başarılı!',
							text: 'Görev başarıyla iptal edildi.',
							icon: 'success',
							confirmButtonText: 'Tamam',
						});
						setTaskList(taskList.filter((item) => item.id !== data.id));
					}
				}
				else {
					if (result.dismiss === Swal.DismissReason.cancel) {
						await Swal.fire('İptal edildi', 'Görev iptal edilmedi :)', 'error');
					}
				}
			});
		};

		const handleDropdown = () => {
			setDropdownShow(!dropdownShow);
			setAnyDropdownIsOpen({
				id: data.id,
			});
		};

		useEffect(() => {
			if (anyDropdownIsOpen.id !== data.id) {
				setDropdownShow(false);
			}
		}, [anyDropdownIsOpen, data.id]);
		return (
			<div className="flex flex-col gap-2">
				<Link href={`/gorevler/detay/${data.id}`}>
					<button className="flex flex-row gap-2 bg-purple-800/80 text-purple-100 hover:bg-purple-700 dark:bg-purple-600/80 dark:hover:bg-purple-500 font-display w-full rounded-xl px-5 py-2 text-left text-sm transition-colors">
						<BiShow className="text-base"></BiShow>
						Görüntüle
					</button>
				</Link>
				{data.task_paired_user !== null && (
					<Link href={`/gorevler/katildiklarim/pair/${data.id}`}>
						<button className="flex flex-row gap-2 bg-blue-800/80 text-blue-100 hover:bg-blue-700 dark:bg-blue-600/80 dark:hover:bg-blue-500 font-display w-full rounded-xl px-5 py-2 text-left text-sm transition-colors">
							<FiUsers className="text-base"></FiUsers>
							Eşleştirmeyi Görüntüle
						</button>
					</Link>
				)}
				{data.state === 0 && (
					<>

						<Link href={`/gorevler/duzenle/${data.id}`}>
							<button className="flex flex-row gap-2 bg-orange-800/80 text-orange-100 hover:bg-orange-700 dark:bg-orange-600/80 dark:hover:bg-orange-500 font-display w-full rounded-xl px-5 py-2 text-left text-sm transition-colors">
								<BiPencil className="text-base"></BiPencil>
								Düzenle
							</button>
						</Link>
						<button onClick={handleCancelTask} className="flex flex-row gap-2 bg-red-600 text-red-100 hover:bg-red-700 dark:bg-red-600/80 dark:hover:bg-red-500 font-display w-full rounded-xl px-5 py-2 text-left text-sm transition-colors">

							<BiExit className="text-base"></BiExit>
							İptal Et
						</button>
					</>
				)}
			</div>
		);
	}
;

export default MyTaskDropdown;
