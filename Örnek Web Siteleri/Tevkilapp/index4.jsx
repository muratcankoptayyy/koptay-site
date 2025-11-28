import React, { useState, useEffect } from 'react';
import request from '@/utils/request';
import { useRouter } from 'next/router';
import Meta from '@/components/Meta';
import Swal from 'sweetalert2';
import { BsArrowLeft, BsCheckCircle, BsClock, BsXCircle, BsGeoAlt, BsPerson, BsCalendar, BsCash } from 'react-icons/bs';
import Link from 'next/link';
import { useSelector } from 'react-redux';
const MyJoinedTasks = () => {
	const router = useRouter();
	const user = useSelector(state => state.user.user);
	const [myTaskList, setMyTaskList] = useState([]);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		fetchMyTasks();
	}, []);

	const fetchMyTasks = async () => {
		try {
			const response = await request('/task/joined-lists', 'GET', null, true);
			if (response.success) {
				console.log(response.data.data);
				setMyTaskList(response.data.data);
			}
		} catch (error) {
			console.error('Görevler yüklenirken hata oluştu:', error);
		} finally {
			setLoading(false);
		}
	};

	const handleTaskAction = async (taskId) => {
		try {
			const response = await request(`/gorevler/${taskId}/islem`, 'POST');
			if (response.success) {
				await Swal.fire({
					icon: 'success',
					title: 'Başarılı',
					text: 'Görev işlemi başarıyla tamamlandı',
					timer: 2000,
					showConfirmButton: false
				});
				fetchMyTasks();
			}
		} catch (error) {
			await Swal.fire({
				icon: 'error',
				title: 'Hata',
				text: error.message || 'Bir hata oluştu',
				confirmButtonText: 'Tamam'
			});
		}
	};

	const getTaskState = (task) => {
		console.log(task);
		if (!task.task_paired_user) return 'Beklemede';
		if (task.task_paired_user.paired_user_id === user?.id) return 'Atandım';
		return 'Farklı kullanıcı atandı';
	};

	return (
		<div className="min-h-screen bg-gradient-to-br from-sky-50 via-blue-50 to-indigo-50 p-4 relative overflow-hidden">
			<Meta title="Katıldığım Görevler" />
			
			{/* Arka plan animasyonları */}
			<div className="absolute inset-0 overflow-hidden">
				<div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-r from-sky-200/30 to-blue-200/30 rounded-full animate-spin-slow"></div>
				<div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-r from-indigo-200/30 to-purple-200/30 rounded-full animate-spin-slow-reverse"></div>
			</div>

			{/* Ana içerik */}
			<div className="relative max-w-[91rem] mx-auto my-24 lg:my-40">
				{/* Başlık ve Geri Butonu */}
				<div className="flex flex-col items-start justify-between mb-8">
					<h1 className="text-xl font-semibold text-gray-800 font-display">Katıldığım Görevler</h1>
					<span className="text-sm text-gray-500">Başvurduğunuz tüm görevleriniz burada listelenmektedir.</span>
					<div className="w-24"></div> {/* Denge için boş div */}
				</div>

				{/* Görev Kartları */}
				<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					{loading ? (
						<div className="col-span-full flex justify-center">
							<div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-violet-500"></div>
						</div>
					) : myTaskList.length > 0 ? (
						myTaskList.map((task) => {
							const taskState = getTaskState(task);
							return (
								<div 
									key={task.id} 
									className="backdrop-blur-xl bg-white/80 rounded-lg shadow-xl p-6 border-3 border-blue-700/20 hover:border-blue-700/50 cursor-pointer hover:shadow-2xl transition-all duration-300"
								>
									{/* Görev Numarası ve Durum */}
									<div className="flex items-center justify-between mb-4">
										<span className="text-sm font-medium text-gray-500">Görev #{task.id}</span>
										{taskState === 'Beklemede' ? (
											<span className="flex items-center gap-1 text-yellow-600">
												<BsClock className="text-lg" />
												<span className="text-sm font-medium">Beklemede</span>
											</span>
										) : taskState === 'Farklı kullanıcı atandı' ? (
											<span className="flex items-center gap-1 text-red-600">
												<BsXCircle className="text-lg" />
												<span className="text-sm font-medium">Farklı kullanıcı atandı</span>
											</span>
										) : (
											<span className="flex items-center gap-1 text-green-600">
												<BsCheckCircle className="text-lg" />
												<span className="text-sm font-medium">Atandım</span>
											</span>
										)}
									</div>

									{/* Görev Başlığı */}
									<h3 className="text-lg font-semibold text-gray-800 mb-2">{task.titleName}</h3>

									{/* Görev İçeriği */}
									<p className="text-gray-600 text-sm mb-4 line-clamp-3">{task.content}</p>

									{/* Görev Detayları */}
									<div className="space-y-3 mb-4">
										{/* Konum */}
										<div className="flex items-center gap-2 text-gray-600">
											<BsGeoAlt className="text-lg" />
											<span className="text-sm">{task.taskLocation}</span>
										</div>

										{/* Görev Tipi */}
										<div className="flex items-center gap-2 text-gray-600">
											<BsPerson className="text-lg" />
											<span className="text-sm">{task.type_text}</span>
										</div>

										{/* Tarih */}
										<div className="flex items-center gap-2 text-gray-600">
											<BsCalendar className="text-lg" />
											<span className="text-sm">{new Date(task.datetime).toLocaleDateString('tr-TR')}</span>
										</div>

										{/* Ücret */}
										<div className="flex items-center gap-2 text-gray-600">
											<BsCash className="text-lg" />
											<span className="text-sm">{task.price} TL</span>
										</div>
									</div>

									{/* İşlem Butonu */}
									{taskState === 'Atandım' && (
										<Link
											href={`/gorevler/katildiklarim/pair/${task.id}`}
											className="w-full block relative group overflow-hidden rounded-xl bg-gradient-to-r from-blue-500 to-indigo-500 p-[2px] transition-all duration-300 hover:from-blue-400 hover:to-indigo-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-white"
										>
											<div className="relative px-6 py-3 bg-white rounded-[10px] transition-all duration-300 group-hover:bg-opacity-0">
												<div className="flex items-center justify-center">
													<span className="flex items-center gap-2 text-blue-500 font-semibold group-hover:text-white">
														<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M18.7 7.2c-.4-.4-1-.4-1.4 0l-7.5 7.5l-3.1-3.1c-.4-.4-1-.4-1.4 0s-.4 1 0 1.4l3.8 3.8c.2.2.4.3.7.3s.5-.1.7-.3l8.2-8.2c.4-.4.4-1 0-1.4"/></svg>
														Görev Detayları</span>
												</div>
											</div>
										</Link>
									)}
								</div>
							);
						})
					) : (
						<div className="col-span-full text-center py-12 flex flex-col items-center justify-center">
							<svg className='text-indigo-800 mb-5' xmlns="http://www.w3.org/2000/svg" width={72} height={72} viewBox="0 0 24 24"><g fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} color="currentColor"><path d="M12.5 22h-3c-3.3 0-4.95 0-5.975-1.08C2.5 19.843 2.5 18.106 2.5 14.633V9.368c0-3.473 0-5.21 1.025-6.289S6.2 2 9.5 2h3c3.3 0 4.95 0 5.975 1.08C19.5 4.157 19.5 5.894 19.5 9.367V12.5M22 16l-3 3m0 0l-3 3m3-3l3 3m-3-3l-3-3"></path><path d="m7 2l.082.493c.2 1.197.3 1.796.72 2.152C8.22 5 8.827 5 10.041 5h1.917c1.213 0 1.82 0 2.24-.355c.42-.356.52-.955.719-2.152L15 2M7 16h4m-4-5h8"></path></g></svg>
							
							<p className="text-gray-800 font-display text-lg">Henüz katıldığınız görev bulunmuyor.</p>
							<p className="text-gray-600">Görevlere katılarak tevkil işlemlerinizi kolayca yönetebilirsiniz.</p>
						</div>
					)}
				</div>
			</div>

			<style jsx global>{`
				@keyframes spin-slow {
					from { transform: rotate(0deg); }
					to { transform: rotate(360deg); }
				}
				@keyframes spin-slow-reverse {
					from { transform: rotate(360deg); }
					to { transform: rotate(0deg); }
				}
				.animate-spin-slow {
					animation: spin-slow 20s linear infinite;
				}
				.animate-spin-slow-reverse {
					animation: spin-slow-reverse 20s linear infinite;
				}
			`}</style>
		</div>
	);
};

export default MyJoinedTasks;