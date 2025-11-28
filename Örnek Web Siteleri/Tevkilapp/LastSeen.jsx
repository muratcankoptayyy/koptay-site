import React, { useEffect } from 'react';
import request from '@/utils/request';
import { useRouter } from 'next/router';

function UpdateLastSeen() {
    const router = useRouter();

    useEffect(() => {
        const updateLastSeen = async () => {
            /*
            try {
                // const response = await request('/user/last-seen', 'POST', {}, true, null);
                if (response.success) {
                    console.log('Son görülme tarihi başarıyla güncellendi.');
                } else {
                    console.error('Son görülme tarihi güncellenirken bir sorun oluştu:', response.message);
                }
            } catch (error) {
                console.error('API isteği sırasında bir hata oluştu:', error);
            }
            */
        };

        if (router.pathname !== '/auth/login') {
            updateLastSeen();
        }
    }, [router.pathname]);

    return null;
}

export default UpdateLastSeen;
