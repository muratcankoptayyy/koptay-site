import React, { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/router';
import {useDispatch} from 'react-redux';
import {login} from '../../redux/slices/userSlice';
import Cookies from 'js-cookie';
import request from '../../utils/request';
import Swal from 'sweetalert2';
import AuthLayout from '../../layouts/AuthLayout';
import Meta from '@/components/Meta';

const Verify2FA = () => {
  const router = useRouter();
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const inputRefs = useRef([]);
  const dispatch = useDispatch();
  
  // Input referanslarını oluştur
  useEffect(() => {
    inputRefs.current = inputRefs.current.slice(0, 6);
  }, []);

  // Input değerlerini güncelle
  const handleInputChange = (index, value) => {
    // Mobil cihazlarda otomatik SMS kodu algılama için
    // Eğer 6 haneli bir kod gelirse (SMS otomatik doldurma)
    if (value.length === 6 && /^\d{6}$/.test(value)) {
      const newCode = value.split('');
      setCode(newCode);
      inputRefs.current[5].focus();
      return;
    }

    // Normal tek karakter girişi
    const newCode = [...code];
    newCode[index] = value.slice(-1); // Son karakteri al (çoklu karakter girişini önle)
    setCode(newCode);

    // Eğer değer girildiyse ve son input değilse bir sonraki inputa geç
    if (value && index < 5) {
      inputRefs.current[index + 1].focus();
    }
  };

  // Geri silme işlemi
  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !code[index] && index > 0) {
      inputRefs.current[index - 1].focus();
    }
  };

  // Yapıştırma işlemi
  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').slice(0, 6);
    if (pastedData.length === 6 && /^\d+$/.test(pastedData)) {
      const newCode = pastedData.split('');
      setCode(newCode);
      inputRefs.current[5].focus();
    }
  };

  // Doğrulama işlemi
  const handleVerify = async () => {
    if (code.some(digit => !digit)) {
      await Swal.fire({
        icon: 'error',
        title: 'Hata',
        text: 'Lütfen tüm alanları doldurun',
        confirmButtonText: 'Tamam',
      });
      return;
    }

    setLoading(true);
    try {
      const response = await request('/auth/login/verify', 'POST', {
        code: code.join(''),
        token: router.query.slug,
      });

      if (response.success) {
        Swal.fire({
          icon: 'success',
          title: 'Başarılı',
          text: 'Giriş işlemi başarılı bir şekilde tamamlandı. Yönlendiriliyorsunuz...',
          confirmButtonText: 'Tamam',
        });

        dispatch(login(response.data));
			  Cookies.set('userToken', response.data.token);
			  Cookies.set('token', response.data.token);
			  Cookies.set('user', JSON.stringify(response.data.user));

        setTimeout(() => {
          if(response.register) {
            router.push('/account-complete');
          } else {
            router.push('/');
          }
        }, 3000);
      } else {
        setLoading(false);
        await Swal.fire({
          icon: 'error',
          title: 'Hata',
          text: response.error || 'Doğrulama kodu hatalı',
          confirmButtonText: 'Tamam',
        });
      }
    } catch (error) {
      setLoading(false);
      await Swal.fire({
        icon: 'error',
        title: 'Hata',
        text: 'Bir hata oluştu',
        confirmButtonText: 'Tamam',
      });
    } finally {
      
    }
  };

  // İptal işlemi
  const handleCancel = () => {
    router.push('/');
  };

  return (
    <AuthLayout>
      <Meta title="Güvenlik Kodu Doğrulama" />
      <div className="min-h-screen bg-gradient-to-br from-sky-50 via-blue-50 to-indigo-50 flex items-center justify-center p-4 relative overflow-hidden">
        {/* Arka plan animasyonları */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-r from-sky-200/30 to-blue-200/30 rounded-full animate-spin-slow"></div>
          <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-r from-indigo-200/30 to-purple-200/30 rounded-full animate-spin-slow-reverse"></div>
        </div>

        {/* Ana içerik */}
        <div className="relative w-full max-w-md">
          <div className="backdrop-blur-xl bg-white/80 rounded-3xl shadow-xl p-8 border border-white/20">
            {/* Başlık */}
            <div className="text-left mb-8">
              <h1 className="text-xl font-bold text-gray-800 mb-2 font-display">
                İki Faktörlü Doğrulama
              </h1>
              <p className="text-gray-600">Telefon numaranıza SMS ile gönderilen 6 haneli doğrulama kodunu giriniz.</p>
            </div>

            {/* Kod giriş alanı */}
            <div className="flex justify-center gap-1 sm:gap-2 mb-8">
              {code.map((digit, index) => (
                <input
                  key={index}
                  ref={el => inputRefs.current[index] = el}
                  type="text"
                  maxLength={index === 0 ? 6 : 1} // İlk input'ta 6 karakter alabilir (SMS otomatik doldurma için)
                  value={digit}
                  onChange={(e) => handleInputChange(index, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(index, e)}
                  onPaste={handlePaste}
                  className="flex-1 max-w-[48px] sm:max-w-[56px] h-12 text-center text-xl sm:text-2xl border-2 border-gray-200 rounded-lg focus:border-sky-500 focus:ring-2 focus:ring-sky-200 outline-none transition-all"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  autoComplete={index === 0 ? "one-time-code" : "off"} // Mobil SMS otomatik doldurma için
                />
              ))}
            </div>

            {/* Doğrula butonu */}
            <button
              onClick={handleVerify}
              disabled={loading}
              className="w-full relative group overflow-hidden rounded-xl bg-gradient-to-r from-sky-500 to-blue-500 p-[2px] transition-all duration-300 hover:from-sky-400 hover:to-blue-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-white disabled:opacity-50 mb-4"
            >
              <div className="relative px-6 py-3 bg-white rounded-[10px] transition-all duration-300 group-hover:bg-opacity-0">
                <div className="flex items-center justify-center">
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-sky-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span className="text-sky-500 font-semibold group-hover:text-white">Doğrulanıyor...</span>
                    </>
                  ) : (
                    <span className="flex items-center gap-2 text-sky-500 font-semibold group-hover:text-white">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><g fill="none"><path d="m12.593 23.258l-.011.002l-.071.035l-.02.004l-.014-.004l-.071-.035q-.016-.005-.024.005l-.004.01l-.017.428l.005.02l.01.013l.104.074l.015.004l.012-.004l.104-.074l.012-.016l.004-.017l-.017-.427q-.004-.016-.017-.018m.265-.113l-.013.002l-.185.093l-.01.01l-.003.011l.018.43l.005.012l.008.007l.201.093q.019.005.029-.008l.004-.014l-.034-.614q-.005-.018-.02-.022m-.715.002a.02.02 0 0 0-.027.006l-.006.014l-.034.614q.001.018.017.024l.015-.002l.201-.093l.01-.008l.004-.011l.017-.43l-.003-.012l-.01-.01z"/><path fill="currentColor" d="M12 2a6 6 0 0 1 5.996 5.775L18 8h1a2 2 0 0 1 1.995 1.85L21 10v10a2 2 0 0 1-1.85 1.995L19 22H5a2 2 0 0 1-1.995-1.85L3 20V10a2 2 0 0 1 1.85-1.995L5 8h1a6 6 0 0 1 6-6m7 8H5v10h14zm-7 2a2 2 0 0 1 1.134 3.647l-.134.085V17a1 1 0 0 1-1.993.117L11 17v-1.268A2 2 0 0 1 12 12m0-8a4 4 0 0 0-4 4h8a4 4 0 0 0-4-4"/></g></svg>
                        Doğrula</span>
                  )}
                </div>
              </div>
            </button>
        
        </div>
        <div className="text-gray-500 text-center my-4">
            veya
        </div>
        <button
            onClick={handleCancel}
            className="w-full text-gray-400 border-gray-300 border-2 hover:border-gray-400 hover:text-gray-500 font-medium transition-colors rounded-xl px-6 py-3"
          >
            Giriş İşlemini İptal Et
          </button>
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
    </AuthLayout>
  );
};

export default Verify2FA;/*   SMS Otomatik Doldurma İçin Önemli Notlar:    1. Android için SMS formatı şu şekilde olmalı:     "123456 verification code for [domain name]"     veya     "[domain name] verification code: 123456"    2. iOS için SMS formatı şu şekilde olmalı:     "Your verification code is: 123456"     veya     "123456 is your verification code"    3. Kod, ilk input alanına otomatik olarak doldurulacak  4. autoComplete="one-time-code" özelliği sadece ilk input'ta aktif  5. maxLength ilk input'ta 6, diğerlerinde 1 olarak ayarlandı  6. Mobil tarayıcılar SMS'i algıladığında otomatik doldurma önerecek*/ 