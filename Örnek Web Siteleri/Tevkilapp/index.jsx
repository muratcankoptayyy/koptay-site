import React, {useCallback} from 'react';
import Benifits from '@/components/dao/Benifits';
import Intro from '@/components/dao/Intro';
import Meta from '@/components/Meta';
import request from '@/utils/request';

const HowWorksPage = () => {
	const [data, setData] = React.useState({});

	const getData = useCallback(async () => {
		const res = await request('/page/nasil-calisir');
		setData(res.data);
	}, []);

	React.useEffect(() => {
		getData();
	}, [getData]);

	return (
		<>
			<Meta title={data.title}/>
			<Intro data={data}/>
			<Benifits/>
		</>
	);
};

export default HowWorksPage;
