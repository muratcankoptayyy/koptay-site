import React, {useState} from 'react';
import {Modal} from '@mui/material';
import request from '@/utils/request';

export const PhoneVerificationModal = ({isOpen, onClose, phone, onVerified}) => {
    const [verificationCode, setVerificationCode] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleVerify = async () => {
        setLoading(true);
        setError('');
        
        // Telefon numarasını temizle
        const cleanPhone = phone.replace(/\D/g, '');
        const phoneWithoutZero = cleanPhone.startsWith('0') ? cleanPhone.slice(1) : cleanPhone;
        
        const response = await request('/phone/verify', 'POST', {
            action: 'verify',
            phone: phoneWithoutZero,
            code: verificationCode
        }, true);

        if (response.success) {
            onVerified();
            onClose();
        } else {
            setError(response.error || 'Doğrulama başarısız oldu.');
        }
        
        setLoading(false);
    };

    return (
        <Modal
            open={isOpen}
            onClose={onClose}
            aria-labelledby="phone-verification-modal"
        >
            <div className="absolute left-2/4 top-2/4 bg-white dark:bg-jacarta-700 rounded-lg p-6 w-96 transform -translate-x-2/4 -translate-y-2/4">
                <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
                    Telefon Numarası Doğrulama
                </h2>
                <p className="text-gray-600 dark:text-gray-300 mb-4">
                    Telefon numaranızı bir kez doğrulamanız yeterli! Sonraki işlemlerinizde bu numarayla tekrar
                    doğrulama yapmanıza gerek kalmaz.
                    <br/>
                    <br/>
                    <span
                        className="block">{phone} numaralı telefonunuza gönderilen 6 haneli doğrulama kodunu giriniz.</span>
                </p>

                <input
                    type="text"
                    maxLength="6"
                    className="w-full px-4 py-2 mb-4 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-jacarta-700 dark:border-jacarta-600 dark:text-white"
                    placeholder="Doğrulama Kodu"
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value)}
                />
                {error && (
                    <p className="text-red-500 mb-4">{error}</p>
                )}
                <div className="flex justify-end gap-2">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-jacarta-600 rounded-lg"
                    >
                        İptal
                    </button>
                    <button
                        onClick={handleVerify}
                        disabled={loading || verificationCode.length !== 6}
                        className="px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent-hover disabled:opacity-50"
                    >
                        {loading ? 'Doğrulanıyor...' : 'Doğrula'}
                    </button>
                </div>
            </div>
        </Modal>
    );
}; 