/* eslint-disable react/no-unescaped-entities */
import {useEffect, useState} from 'react';
import {
	Accordion,
	AccordionHeader,
	AccordionBody,
} from '@material-tailwind/react';
import request from '../../utils/request';

function Icon({id, open}) {
	return (
		<svg
			xmlns="http://www.w3.org/2000/svg"
			className={`${
				id === open ? 'rotate-180' : ''
			} h-5 w-5 transition-transform`}
			fill="none"
			viewBox="0 0 24 24"
			stroke="currentColor"
			strokeWidth={2}
		>
			<path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7"/>
		</svg>
	);
}

const FaqAccordion = () => {
	const [open, setOpen] = useState(1);
	const [List, setList] = useState([]);

	const fetchData = async () => {

		const {data, success} = await request('/faq/home', 'GET', null, true, false, true, 250);
		if (success) {
			let temp_datas = [];

			data.map((item) => {
				temp_datas.push({
					title: item.title,
					content: item.content,
					id: item.id,
				});
			});

			setList(temp_datas);
		}
	};

	useEffect(() => {
		fetchData();
	}, []);

	const handleOpen = (value) => {
		setOpen(open === value ? 1 : value);
	};

	return (
		<div className="mb-8">
			{List.map((item) => {
				const {id, title, content} = item;
				return (
					<Accordion
						className="mb-5 overflow-hidden rounded-lg border border-jacarta-100 dark:border-jacarta-600"
						open={open === id}
						key={id}
						icon={<Icon id={id} open={open}/>}
					>
						<AccordionHeader
							className="border-b-0 accordion-button relative flex w-full items-center justify-between bg-white px-4 py-3 text-left font-display text-jacarta-700 dark:bg-jacarta-700 dark:text-white text-md !mb-0"
							onClick={() => handleOpen(id)}
						>
							{title}
						</AccordionHeader>
						<AccordionBody className="accordion-body border-t border-jacarta-100 bg-white p-4 dark:border-jacarta-600 dark:bg-jacarta-700 text-base dark:text-gray-200 h-full">
							<div dangerouslySetInnerHTML={{__html: content}}></div>
						</AccordionBody>
					</Accordion>
				);
			})}
		</div>
	);
};

export default FaqAccordion;
