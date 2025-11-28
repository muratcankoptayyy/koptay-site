import ListPostItems from './list-content';

const Collections = ({ticketList, loading}) => {
	return (
		<div className="tab-content">
			{/* List */}
			<div
				className="tab-pane fade show active"
			>
				<div className="scrollbar-custom overflow-x-auto">
					<div
						role="table"
						className="w-full min-w-[736px] border border-jacarta-100 bg-white text-sm dark:border-jacarta-600 dark:bg-jacarta-700 dark:text-white rounded-2lg"
					>
						<div
							className="flex rounded-t-2lg bg-jacarta-50 dark:bg-jacarta-600"
							role="row"
						>
							<div className="w-1/12 py-3 px-4" role="columnheader">
                                <span className="overflow-hidden text-ellipsis text-jacarta-700 dark:text-jacarta-100">
                                    Talep No
                                </span>
							</div>
							<div className="text-center w-4/12 py-3 px-4" role="columnheader">
                                <span className="w-72 text-center overflow-hidden text-jacarta-700 dark:text-jacarta-100">
                                    Başlık
                                </span>
							</div>
							<div
								className="w-2/12 py-3 px-4 text-center"
								role="columnheader"
							>
                                <span className="w-24 text-center overflow-hidden text-ellipsis text-jacarta-700 dark:text-jacarta-100">
                                    Kategori
                                </span>
							</div>
							<div
								className="w-2/12 py-3 px-4 text-center"
								role="columnheader"
							>
                                <span className="w-48 overflow-hidden text-ellipsis text-jacarta-700 dark:text-jacarta-100">
                                    Durum
                                </span>
							</div>
							<div
								className="w-2/12 py-3 px-4 text-center"
								role="columnheader"
							>
                                <span className=" overflow-hidden text-ellipsis text-jacarta-700 dark:text-jacarta-100">
                                    Oluşturulma Tarihi
                                </span>
							</div>
							<div
								className="w-1/12 py-3 px-4 text-center"
								role="columnheader"
							>
                                <span className="w-full overflow-hidden text-ellipsis text-jacarta-700 dark:text-jacarta-100">
                                    İşlem
                                </span>
							</div>
						</div>
						<ListPostItems ticketList={ticketList} loading={loading}/>
					</div>
				</div>
			</div>
		</div>
	);
};

export default Collections;
