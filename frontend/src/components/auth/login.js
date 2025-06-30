import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { authService } from '../../services/authService';

const LoginPage = () => {
  const router = useRouter();

  useEffect(() => {
    async function checkAuth() {
      const user = await authService.getCurrentUser();
      if (user) {
        router.push('/dashboard');
      }
    }
    checkAuth();
  }, [router]);

  return (
    <div className="auth-page">
      <h1>Accedi al tuo account</h1>
      <LoginForm />
    </div>
  );
};

export default LoginPage;

import LoginForm from '../../components/auth/LoginForm';
