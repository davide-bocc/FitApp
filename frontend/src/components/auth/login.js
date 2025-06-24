import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import useAuth from '../../hooks/useAuth';
import LoginForm from '../../components/auth/LoginForm';

const LoginPage = () => {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [isRedirecting, setIsRedirecting] = useState(false);

  useEffect(() => {
    if (!loading && user && !isRedirecting) {
      setIsRedirecting(true);
      router.push('/dashboard');
    }
  }, [user, loading, isRedirecting]);

  if (loading || isRedirecting) {
    return <div>Caricamento...</div>;
  }

  return (
    <div className="auth-page">
      <h1>Accedi al tuo account</h1>
      <LoginForm />
    </div>
  );
};

export default LoginPage;