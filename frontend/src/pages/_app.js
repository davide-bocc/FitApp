import { useEffect } from 'react';
import { useRouter } from 'next/router';

function MyApp({ Component, pageProps }) {
  const router = useRouter();

  useEffect(() => {
    // Verifica ad ogni cambio route se il token esiste
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    console.log('Token attuale:', token);

    if (!token && !router.pathname.startsWith('/auth')) {
      router.push('/auth/login');
    }
  }, [router.pathname]);

  return <Component {...pageProps} />;
}

export default MyApp;