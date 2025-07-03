import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import { authService } from '../../services/authService';

export default function AuthGuard({ children }) {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    async function checkAuth() {
      try {
        const user = await authService.getCurrentUser();
        if (!user) {
          router.push('/auth/login');
          return;
        }
        setAuthenticated(true);
      } catch {
        router.push('/auth/login');
      } finally {
        setLoading(false);
      }
    }
    checkAuth();
  }, [router]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!authenticated) {
    return null;
  }

  return children;
}
