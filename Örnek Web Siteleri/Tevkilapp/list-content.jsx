import Link from 'next/link';
import moment from 'moment';
import {BsLifePreserver} from 'react-icons/bs';

const ListPostItems = ({ticketList, loading}) => {

	return (
		<>
			{loading ? (
				<div className="flex justify-center items-center">
					<div className="flex flex-col items-center justify-center">
						<h1 className="text-2xl font-semibold mt-10 mb-20 text-jacarta-700 dark:text-white">
							Destek Talepleri Yükleniyor.
						</h1>

					</div>
				</div>
			) : (
				<>
					{ticketList.length > 0 ? (
						<>
							{ticketList.map((ticket) => (
								<div
									key={ticket.id}
									className="flex transition-shadow hover:shadow-lg px-1"
									role="row"
								>
									<div
										className="flex w-1/12 items-center border-t border-jacarta-100 py-4 px-4 dark:border-jacarta-600"
										role="cell"
									>
										<span className="mr-3 lg:mr-5">{ticket.id}</span>
									</div>
									<div
										className="flex justify-center items-center w-4/12 whitespace-nowrap border-t border-jacarta-100 py-4 px-4 dark:border-jacarta-600"
										role="cell"
									>
					         <span className="text-sm w-72 text-center font-medium tracking-tight">
					             {ticket.title.length > 30 ? ticket.title.slice(0, 30) + '...' : ticket.title}
					         </span>
									</div>
									<div
										className="flex justify-center w-2/12 items-center border-t border-jacarta-100 py-4 px-4 dark:border-jacarta-600"
										role="cell"
									>
					         <span className="text-sm font-medium w-24 text-center tracking-tight">
										{ticket.category != null ? ticket.category.name : 'Belirtilmemiş'}
					         </span>
									</div>
									<div
										className="flex justify-center w-2/12 items-center border-t border-jacarta-100 py-4 px-4 dark:border-jacarta-600"
										role="cell"
									>
										 <span className={`p-1 rounded-lg w-48 text-center font-semibold text-white ${ticket.state === 'Cevaplandı' ? 'bg-green' : ticket.state === 'Cevap Bekliyor' ? 'bg-yellow-700' : 'bg-red-500'} `}>
					             {ticket.state}
					         </span>
									</div>
									<div
										className="flex justify-center w-2/12 items-center border-t border-jacarta-100 py-4 px-4 dark:border-jacarta-600"
										role="cell"
									>
										<span className="text-sm font-medium tracking-tight">{moment.utc(ticket.createdAt).format('DD.MM.YYYY')}</span>
									</div>
									<div
										className="flex text-center justify-center w-1/12 items-center border-t border-jacarta-100 py-4 px-4 dark:border-jacarta-600"
										role="cell"
									>
										<Link href={`/destek/detay/${ticket.id}`}>
											<button
												type="submit"
												className="bg-accent shadow-accent-volume hover:bg-accent-dark rounded-full py-3 px-8 text-center font-semibold text-white transition-all"
												id="contact-form-submit"
											>
												Detay
											</button>
										</Link>
									</div>
								</div>
							))}
						</>
					) : (
						<div className="flex flex-col items-center justify-center">
							<BsLifePreserver className="text-[5rem] text-jacarta-400 dark:text-jacarta-600 mt-10 mb-3"/>
							<h1 className="text-lg font-semibold text-jacarta-700 dark:text-white">
								Destek Talebiniz Bulunmamaktadır.
							</h1>
							<p className="text-sm text-jacarta-500 dark:text-jacarta-400 mb-20">
								Destek talebi oluşturmak için sağ üst taraftaki butona tıklayabilirsiniz.
							</p>
						</div>
					)}
				</>
			)}

		</>
	);
};

export default ListPostItems;
