const API_URL = 'https://api.tevkilapp.com/api';
// const API_URL = 'http://127.0.0.1:8000/api';

const request = (url, method, data, authorization = false, formData, cache, cacheTime) => {
	const token = authorization ? localStorage.getItem('userToken') : null;

	const options = {
		method,
		headers: {
			'Content-Type': 'application/json',
			'Authorization': authorization ? `Bearer ${token}` : '',
		},
		mode: 'cors',
	};

	const formDataOptions = {
		method,
		headers: {
			'Authorization': authorization ? `Bearer ${token}` : '',
		},
		mode: 'cors',
	};

	if (data) {
		if (formData) {
			formDataOptions.body = data;
		}
		else {
			options.body = JSON.stringify(data);
		}
	}
	const nowDate = new Date();
	const expireTime = nowDate.getTime() + cacheTime * 100;

	if (cache && method === 'GET') {
		const cacheTitle = `${url}-${method}`;
		const cacheData = JSON.parse(localStorage.getItem(cacheTitle));
		if (cacheData) {
			// cache'in süresi dolmamışsa
			if (nowDate.getTime() < cacheData.expireTime) {
				return new Promise((resolve, reject) => {
					resolve(cacheData);
				});
			}
			else {
				// cache'in süresi dolmuşsa cache silinir ve istek atılır
				localStorage.removeItem(cacheTitle);
				return requestWithCache(url, formData, formDataOptions, options, cacheTitle, expireTime);

			}
		}
		else {
			//hali hazırda cache yoksa istek atıp gelen cacheTime'a göre cache oluşturulacak
			return requestWithCache(url, formData, formDataOptions, options, cacheTitle, expireTime);

		}
	}
	else {
		//cache'e gerek yoksa direk istek atılır
		return fetch(`${API_URL}${url}`, formData ? formDataOptions : options)
		.then(response => {
			if (response.ok) {
				return response.json();
			}
			else {
				return response.json().then(err => {
					return err;
				});
			}
		});
	}

};

const requestWithCache = async (url, formData, formDataOptions, options, cacheTitle, expireTime) => {
	return fetch(`${API_URL}${url}`, formData ? formDataOptions : options)
	.then(async (response) => {
		if (response.ok) {
			const jsonData = await response.json();
			localStorage.setItem(cacheTitle, JSON.stringify({
				data: jsonData.data,
				message: jsonData.message,
				success: jsonData.success,
				expireTime,
			}));
			return jsonData;
		}
		else {
			return response.json().then(err => {
				return err;
			});
		}
	});
};

export default request;