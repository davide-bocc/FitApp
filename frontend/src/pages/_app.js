import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { tokenService } from '../services/api';
import { authService } from '../services/authService';

// Componente di monitoraggio
const TokenGuard = ({ children }) => {
  const router = useRouter();

  useEffect(() => {
    // 1. Pulizia iniziale
    authService.cleanAllStorage();
    tokenService.clearAllLegacyTokens();

    // 2. Controllo token ogni 5 secondi (solo in sviluppo)
    if (process.env.NODE_ENV === 'development') {
      const interval = setInterval(() => {
        if (localStorage.getItem('Manual_Token')) {
          console.error('⚠️ MANUAL_TOKEN DETECTED!');
          authService.cleanAllStorage();
          window.location.reload();
        }
      }, 5000);
      return () => clearInterval(interval);
    }
  }, []);

  useEffect(() => {
    const checkAuth = async () => {
      const isAuthPage = router.pathname.startsWith('/auth');

      if (!tokenService.isValid() && !isAuthPage) {
        authService.cleanAllStorage();
        router.push('/auth/login?session_expired=1');
      }
    };

    checkAuth();
  }, [router.pathname]);

  return children;
};

function MyApp({ Component, pageProps }) {
  return (
    <TokenGuard>
      <Component {...pageProps} />
    </TokenGuard>
  );
}

export default MyApp;
