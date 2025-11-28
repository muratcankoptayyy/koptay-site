import request from './request';
import { store } from '../redux/store';
import { setNotifications, setLoading, setError } from '../redux/slices/notificationSlice';

export const kalanZaman = (date) => {
	let today = new Date();
	let dateToCompare = new Date(date);
	let diffTime = dateToCompare - today;

	let diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
	diffTime = diffTime - diffDays * (1000 * 60 * 60 * 24);

	let diffHours = Math.floor(diffTime / (1000 * 60 * 60));
	diffTime = diffTime - diffHours * (1000 * 60 * 60);

	let diffMinutes = Math.floor(diffTime / (1000 * 60));
	diffTime = diffTime - diffMinutes * (1000 * 60);

	let diffSeconds = Math.floor(diffTime / (1000));

	let result = '';

	if (diffDays > 0) {
		result += `${diffDays} gün `;

		if (diffHours > 0) {
			result += `${diffHours} saat `;
		}
	}
	else {
		if (diffHours > 0) {
			result += `${diffHours} saat `;

			if (diffMinutes > 0) {
				result += `${diffMinutes} dakika `;
			}
		}
		else {
			if (diffMinutes > 0) {
				result += `${diffMinutes} dakika `;

				if (diffSeconds > 0) {
					result += `${diffSeconds} saniye `;
				}
			}
			else {
				if (diffSeconds > 0) {
					result += `${diffSeconds} saniye `;
				}
			}
		}
	}

	return result + 'sonra';
};

export const formatNumber = (number) => {
	const parts = number.toString().split('.');
	parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');

	return parts;
};

export const handleDateFormat = (date) => {
	const originalDate = new Date(date); // İlk tarih
	return `${originalDate.getDate()}.${originalDate.getMonth() + 1}.${originalDate.getFullYear()} ${originalDate.getHours()}:${originalDate.getMinutes()}`;
};

export const refreshNotifications = async () => {
	try {
		// Redux loading state'ini güncelle
		store.dispatch(setLoading(true));
		store.dispatch(setError(null));
		
		// LocalStorage'dan bildirimleri temizle
		localStorage.removeItem('notifications');
		localStorage.removeItem('notificationsLastFetch');
		
		console.log('Bildirimler temizlendi, yeniden çekiliyor...');
		
		// API'den bildirimleri yeniden çek
		const response = await request('/user/notifications', 'GET', null, true);
		
		if (response && response.success && Array.isArray(response.data)) {
			const formattedNotifications = response.data.map(notification => ({
				id: notification.id || Math.random().toString(36).substr(2, 9),
				title: notification.title || 'Bildirim',
				message: notification.message || '',
				link: notification.link || null,
				read: notification.read || false,
				icon: notification.icon || 'default',
				submessage: notification.submessage || null
			}));
			
			// Redux state'ini güncelle
			store.dispatch(setNotifications(formattedNotifications));
			
			// LocalStorage'a kaydet
			localStorage.setItem('notifications', JSON.stringify(formattedNotifications));
			localStorage.setItem('notificationsLastFetch', new Date().getTime().toString());
			
			console.log('Bildirimler başarıyla yenilendi');
			return formattedNotifications;
		} else {
			store.dispatch(setError('API yanıtı geçersiz format'));
			return null;
		}
	} catch (error) {
		console.error('Bildirimler yenilenirken hata:', error);
		store.dispatch(setError(error.message));
		return null;
	} finally {
		store.dispatch(setLoading(false));
	}
};