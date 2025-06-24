import AuthGuard from '../components/auth/AuthGuard';

export default function Dashboard() {
  return (
    <AuthGuard>
      <h1>Benvenuto nella tua dashboard</h1>
    </AuthGuard>
  );
}