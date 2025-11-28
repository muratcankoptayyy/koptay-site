import React, { useState } from 'react';
import { refreshNotifications } from '@/utils/helper';
import { request } from '@/utils/request';

const NotificationMobile = ({ notifications, setNotifications, setShowLocationModal }) => {
  const [isOpen, setIsOpen] = useState(false);



  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      setIsOpen(false);
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'area':
        return (
          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
            <svg className="w-7 h-7 text-blue-600" xmlns="http://www.w3.org/2000/svg" width={48} height={48} viewBox="0 0 24 24"><path fill="currentColor" fillRule="evenodd" d="M4.146 21.682c1.39 1.39 3.38 1.39 7.36 1.39h1c3.98 0 5.97 0 7.36-1.39s1.39-3.39 1.39-7.36v-4c0-3.98 0-5.97-1.39-7.36s-3.38-1.39-7.36-1.39h-.5c-.41 0-.75.34-.75.75s.34.75.75.75h.5c3.56 0 5.35 0 6.3.95s.95 2.74.95 6.3v4c0 3.56 0 5.35-.95 6.3s-2.74.95-6.3.95h-1c-3.56 0-5.35 0-6.3-.95s-.95-2.74-.95-6.3v-5c0-.41-.34-.75-.75-.75s-.75.34-.75.75v5c0 3.98 0 5.97 1.39 7.36m9.36-3.61h4c.41 0 .75-.34.75-.75s-.34-.75-.75-.75h-4c-.41 0-.75.34-.75.75s.34.75.75.75m4-10h-4c-.41 0-.75-.34-.75-.75s.34-.75.75-.75h4c.41 0 .75.34.75.75s-.34.75-.75.75m-4 5h4c.41 0 .75-.34.75-.75s-.34-.75-.75-.75h-4c-.41 0-.75.34-.75.75s.34.75.75.75m-5.5 6c-.3 0-.57-.18-.69-.45c-.351-.816-.936-1.046-1.012-1.077l-.008-.003a.76.76 0 0 1-.5-.93c.12-.39.52-.62.91-.51c.09.02.61.18 1.15.69c.54-1.05 1.47-2.47 2.82-3.14c.37-.19.82-.03 1.01.34s.04.82-.34 1.01c-1.69.85-2.61 3.54-2.62 3.57c-.1.29-.37.5-.68.51h-.03zm-1.45-10.22c.15.15.34.22.53.22s.38-.08.53-.22s.41-.35.72-.6c1.42-1.15 2.42-2.02 2.42-2.93s-1-1.79-2.42-2.93c-.31-.24-.57-.45-.72-.6a.754.754 0 0 0-1.06 0c-.29.29-.29.77 0 1.06c.17.17.47.42.83.71l.141.116c.288.235.701.572 1.05.894h-5.08c-.41 0-.75.34-.75.75s.34.75.75.75h5.08c-.41.38-.9.78-1.19 1.01l-.17.14c-.279.23-.519.428-.66.57c-.29.29-.29.77 0 1.06" color="currentColor"></path></svg>
          </div>
        );
      case 'premium':
        return (
          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center">
            <svg className="w-7 h-7 text-yellow-600" xmlns="http://www.w3.org/2000/svg" width={48} height={48} viewBox="0 0 24 24"><path fill="currentColor" d="M10.277 16.515c.005-.11.186-.154.24-.058c.254.45.686 1.111 1.176 1.412s1.276.386 1.792.408c.11.005.153.186.057.24c-.45.254-1.11.686-1.411 1.176s-.386 1.276-.408 1.792c-.005.11-.187.153-.24.057c-.254-.45-.686-1.11-1.177-1.411c-.49-.301-1.276-.386-1.791-.408c-.11-.005-.154-.187-.058-.24c.45-.254 1.111-.686 1.412-1.177c.3-.49.386-1.276.408-1.791"></path><path fill="currentColor" d="M18.492 15.515c-.009-.11-.2-.156-.258-.062c-.172.283-.42.623-.697.793s-.692.236-1.022.262c-.11.008-.156.2-.062.257c.282.172.623.42.793.697s.236.693.262 1.023c.008.11.2.155.257.061c.172-.282.42-.623.697-.792s.693-.237 1.023-.262c.11-.009.155-.2.061-.258c-.282-.172-.623-.42-.792-.697s-.237-.692-.262-1.022" opacity={0.5}></path><path fill="currentColor" d="m14.703 4.002l-.242-.306c-.937-1.183-1.405-1.775-1.95-1.688c-.544.088-.805.796-1.326 2.213l-.135.366c-.148.403-.222.604-.364.752s-.336.225-.724.38l-.353.141l-.247.1c-1.2.48-1.804.753-1.882 1.283c-.082.565.49 1.049 1.634 2.016l.296.25c.326.275.488.413.581.6c.094.187.107.403.133.835l.024.393c.094 1.52.14 2.28.635 2.542c.494.262 1.108-.147 2.336-.966l.318-.212c.349-.233.523-.35.723-.381s.401.024.806.136l.367.102c1.423.394 2.134.591 2.521.188c.388-.403.195-1.14-.19-2.613l-.1-.381c-.109-.419-.164-.628-.134-.835s.142-.389.366-.752l.203-.33c.785-1.276 1.178-1.914.924-2.426c-.255-.51-.988-.557-2.454-.648l-.38-.024c-.416-.026-.624-.039-.805-.135s-.314-.264-.58-.6"></path><path fill="currentColor" d="M8.835 13.326C6.698 14.37 4.919 16.024 4.248 18c-.752-4.707.292-7.747 1.965-9.637c.144.295.332.539.5.73c.35.396.852.82 1.362 1.251l.367.31l.17.145c.005.064.01.14.015.237l.03.485c.04.655.08 1.294.178 1.805" opacity={0.5}></path></svg>
          </div>
        );
      case 'premium-red':
        return (
          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center">
            <svg className="w-7 h-7 text-slate-600" xmlns="http://www.w3.org/2000/svg" width={48} height={48} viewBox="0 0 16 16"><path fill="currentColor" d="M2 10c0 1.803 1.555 3.653 4.222 3.957a5.5 5.5 0 0 1-.72-1.157C3.882 12.333 3 11.128 3 10v-.5a.5.5 0 0 1 .5-.5h1.707q.149-.524.393-1H3.5A1.5 1.5 0 0 0 2 9.5zm7.75-5.75q-.001.429-.124.82a5.5 5.5 0 0 0-1.385.414a1.75 1.75 0 1 0-.836.47a5.5 5.5 0 0 0-1.078.963A2.751 2.751 0 1 1 9.75 4.25M15 10.5a4.5 4.5 0 1 1-9 0a4.5 4.5 0 0 1 9 0m-4.024-2.64a.494.494 0 0 0-.952 0l-.477 1.532H8c-.484 0-.686.647-.294.944l1.25.947l-.477 1.532c-.15.48.378.88.77.583l1.25-.947l1.25.947c.392.297.92-.103.77-.583l-.477-1.532l1.25-.947c.392-.297.19-.944-.294-.944h-1.546z"></path></svg>
          </div>
        );
      case 'barocard':
        return (
          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
            <svg className="w-7 h-7 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
        );
        case 'email':
          return (
            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-sky-100 flex items-center justify-center">
              <svg className="w-7 h-7 text-sky-600" xmlns="http://www.w3.org/2000/svg" width={24} height={24} viewBox="0 0 24 24"><path fill="currentColor" d="m15.489 21.27l-3.558-3.558l.708-.708l2.85 2.85l5.688-5.688l.708.707zM3 19V5h18v6.542l-5.506 5.487l-2.855-2.856l-3.533 3.533L10.4 19zm9-6.884l8-5.231L19.692 6L12 11L4.308 6L4 6.885z"></path></svg>
            </div>
          );
      case 'giveaway':
        return (
          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center">
            <svg className="w-8 h-8" xmlns="http://www.w3.org/2000/svg" width={48} height={48} viewBox="0 0 128 128"><path fill="#f5b03e" d="M16.4 31.73s-6.45.51-7.31 1.96c-.87 1.45-.92 3.68-.92 6.13c0 2.46-.1 8.1-.1 8.1l1.54 3.31s.29 42.19.29 43.5c0 1.3 0 2.89 1.88 3.9s49.66 24.09 51.15 24.71c2.25.93 3.32.58 3.32.58l53.09-88.79s-.17-2.43-2.38-3.01c-1.27-.32-100.56-.39-100.56-.39"></path><path fill="#e07f14" d="M65.68 60.92c-.81 2.23-.44 25.29-.3 42.06c.14 16.76-.43 20.23 0 20.81s1.6.02 4.91-1.45c6.15-2.72 35.69-17.34 37.86-18.64s7.47-3.99 8.34-5.44s1.34-14.94 1.63-25.77c.29-10.84.58-19.51.58-19.51l1.3-3.9s-.28-10.54-.33-11.7c-.09-1.92-.3-2.91-.79-2.67c-.7.33-6.54 5.12-22 12.64c-9.71 4.71-30.64 12.03-31.2 13.57"></path><path fill="#fdd717" d="M65.82 11.21c-4.33-.2-16.18 6.65-27.6 10.4S9.56 32.9 9.41 33.34c-.14.43 6.94 3.6 11.46 5.77c5.37 2.57 25.87 12.28 29.62 13.87c3.76 1.59 12.72 5.31 14.16 5.2c2.02-.14 21.1-7.66 30.78-12.28s21.78-11.78 21.94-13.52c.07-.78-17.8-7.45-26.71-11.48c-17.2-7.79-21.67-9.54-24.84-9.69"></path><path fill="#e37d14" d="M8.12 49.77c.15 1.88 1.18 2.55 3.8 3.69s52.15 26.87 53.29 26.87s1.48-4.08.23-3.97c-.68.06-16.95-7.67-32.15-15.39C20.39 54.43 8.04 47.9 8.04 47.9z"></path><path fill="#ba5e0d" d="M120.01 48.99S67.12 75.89 66.6 76.15s-1.35.17-1.35.17l-.04 4.01s.49.11 1.04-.06c.32-.1 52.23-26.97 52.46-27.05s1.23-.68 1.44-1.95c.18-1.02-.14-2.28-.14-2.28"></path><path fill="#af0f1b" d="m28.86 97.42l10.35 15.4l4.53 1.55s.37-16.8.52-29.25c.21-18.19.13-34.78.39-35.72c.43-1.59 20.56-8.12 20.56-8.12S87.95 48.41 88.67 50c.32.7.07 12.48 0 26.21c-.09 17.34-.06 37.36-.06 37.36s2.35-.01 2.63-.88c.29-.87 1.45-7.58 1.45-7.58l8.82-58.79l4.48-5.78l-6.22-11.84l-25.52-12.56l-8.77 1.97l-9.49-1.45l-30.1 21.63l3.51 7.12l8.61 4.39z"></path><path fill="#dc0d28" d="M91.28 49.39c-.55 1.21-.23 63.56-.23 63.56s2.75-1.52 6.29-3.22c3.52-1.69 6.05-2.74 6.27-3.62s.61-62.54.61-62.54z"></path><path fill="#ff2a23" d="M41.35 48.1c.33.36-.21 65.06-.88 65.21c-.53.13-12.58-5.25-12.58-5.8s.97-62.38.97-62.38S40.37 47 41.35 48.1m23.88-33.85c-3.33 0-7.01.95-8.08 3.74s-1.31 6.94-1.31 10.04c0 2.97-.48 10.57 8.67 10.45s9.42-3.51 9.56-10.99c.12-6.24-.71-9.27-1.54-10.57c-.74-1.17-3.2-2.67-7.3-2.67"></path><path fill="#fcc9d2" d="M59.94 29.69c2.08.12 2.97-4.45 4.57-6.95c1.6-2.49 3.27-4.16 2.67-5.46c-.49-1.08-4.84-1.43-7.19 1.84c-1.65 2.31-1.94 10.46-.05 10.57"></path><path fill="#ff2a23" d="M73.33 16.42s2.95 3 3.72 8.88s-.12 10.45-.12 10.45s14.66-.44 19.72.53c4.99.97 6.73 3.17 6.73 4.77s-3.28 2.89-6.61 2.65s-5.58-.42-6 .42s.18 2.14 4.81 2.49c4.63.36 9.98-.3 11.64-6.06s1.72-15.74 1.13-22.93s-1.89-11.3-5.11-12.86c-3.39-1.63-11.88-1.9-19.9 2.61s-10.01 9.05-10.01 9.05"></path><path fill="#fcc9d2" d="M89.94 9.58c-1.04-1.34-4.39-1.3-6.18.77c-1.9 2.2-2.32 10.57.12 11.05c2.76.54 2.26-3.98 4.28-6.77c1.98-2.73 2.79-3.74 1.78-5.05"></path><path fill="#ff2a23" d="M56.38 16.71S45.15 3.62 32.32 3.82c-7.72.12-9.68 4.57-10.1 6.41s-3.62 20.14.65 30.05S36 47.62 37.39 47.3c1.78-.42 5.57-1.72 5.21-3.09s-12.95 3.56-13.07-2.08s8.91-6.24 13.07-6.36s11.29.83 11.29.83s-1.25-6.83-.42-11.7s2.91-8.19 2.91-8.19"></path><path fill="#fcc9d2" d="M28.88 8.57c-1.6 1.66-2.26 11.23-1.25 15.98s1.9 6.77 3.98 6.36c1.74-.35 2.79-9.67 3.62-12.95c.89-3.5 3.09-7.22 2.2-8.85c-1.36-2.5-6.88-2.27-8.55-.54"></path></svg>
          </div>
        );
      default:
        return (
          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
            <svg className="w-7 h-7 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        );
    }
  };

  return (
    <>
      <div className="flex flex-col items-center relative" onClick={() => setIsOpen(true)}>
        <svg className="w-6 h-6" xmlns="http://www.w3.org/2000/svg" width={48} height={48} viewBox="0 0 24 24">
          <path fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 8.4c0-1.697-.632-3.325-1.757-4.525S13.59 2 12 2s-3.117.674-4.243 1.875C6.632 5.075 6 6.703 6 8.4C6 15.867 3 18 3 18h18s-3-2.133-3-9.6M13.73 21a2 2 0 0 1-3.46 0"></path>
        </svg>
        {notifications.filter(n => !n.read).length > 0 && (
          <span className="absolute top-0 inline-flex items-center justify-center w-5 h-5 text-sm font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-500 rounded-full">
            {notifications.filter(n => !n.read).length}
          </span>
        )}
        <span className="text-xs text-black dark:text-white/90">Bildirimler</span>
      </div>

      {isOpen && (
        <div className="fixed inset-0 flex h-full p-0 top-0 border-b pb-[72px]" onClick={handleOverlayClick}>
          <div className="w-full max-w-lg bg-white">
            <div className="flex items-center justify-between p-4 border-b border-gray-100">
              <h3 className="text-lg font-semibold text-gray-800 font-display">Bildirimler</h3>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 text-gray-400 hover:text-gray-500"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="max-h-[calc(100vh-8rem)] overflow-y-auto pt-5">
              {notifications.length > 0 ? (
                notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className="px-4 py-3 hover:bg-gray-50 cursor-pointer mb-3 border-b border-gray-100"
                    onClick={() => {
                      if (notification.icon === 'area') {
                        setShowLocationModal(true);
                      } else if (notification.link) {
                        window.location.href = notification.link;
                      }
                    }}
                  >
                    <div className="flex items-start space-x-4">
                      {getIcon(notification.icon)}
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900 font-display">
                          {notification.title}
                        </p>
                        <p className="text-sm text-gray-600 mt-1">
                          {notification.message}
                        </p>
                        {notification.submessage && (
                          <p className="text-xs text-orange-600 px-2 py-1 rounded-lg bg-orange-100/90 mt-1 inline-block">
                            {notification.submessage}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="px-4 py-3 text-center text-gray-500">
                  <div className='flex flex-col items-center justify-center my-5 gap-6'>
                    <svg xmlns="http://www.w3.org/2000/svg" width={72} height={72} viewBox="0 0 24 24">
                      <g fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}>
                        <path d="M10.568 2.975a2.06 2.06 0 0 0-.73 1.27a1 1 0 0 1-.2.42a1 1 0 0 1-.36.3l-.79.38a5.1 5.1 0 0 0-1.65 1.29c-1.4 1.67-1.4 2.42-1.4 5.27c0 1.29-1.37 2.46-1.73 3.62c-.22.69-.34 2.25 1.48 2.25h13.58a1.6 1.6 0 0 0 .77-.16a1.64 1.64 0 0 0 .6-.51a1.6 1.6 0 0 0 .27-.73a1.6 1.6 0 0 0-.13-.78c-.36-1.09-1.79-2.39-1.79-3.68v-2.13"></path>
                        <path d="M15.228 17.775c.003.427-.075.851-.23 1.25a3.4 3.4 0 0 1-.71 1.06a3.2 3.2 0 0 1-2.33.94a3.2 3.2 0 0 1-1.26-.25a3.3 3.3 0 0 1-1.77-1.77a3.2 3.2 0 0 1-.23-1.23m1.45-8.85h4.24a.19.19 0 0 1 .14.32l-4.06 4.06a.19.19 0 0 0 .035.289a.2.2 0 0 0 .105.03h4.24m-.75-10.459h2.69a.1.1 0 0 1 .096.119a.1.1 0 0 1-.026.05l-2.59 2.59a.1.1 0 0 0 .015.153a.1.1 0 0 0 .055.018h2.66"></path>
                      </g>
                    </svg>
                    <div>
                      <div className='font-display text-lg text-gray-800'>Bildirim bulunmuyor.</div> 
                      <div className='text-base text-gray-500'>Bildirimlerinizi buradan takip edebilirsiniz.</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            {/* <button className='bg-blue-500 text-white p-2 rounded-lg px-6 py-2 ml-4' onClick={refreshNotifications}>Bildirimleri Yenile</button> */}
          </div>
        </div>
      )}
    </>
  );
};

export default NotificationMobile;
