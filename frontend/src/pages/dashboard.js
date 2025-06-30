import { useRouter } from 'next/router';
import { useAuth } from '../../contexts/AuthContext';
import AuthGuard from '../components/auth/AuthGuard';
import WorkoutForm from '../../components/workouts/WorkoutForm';

export default function Dashboard() {
  const { user } = useAuth();
  const router = useRouter();

  if (!user) {
    return <div>Caricamento...</div>;
  }

  return (
    <AuthGuard>
      {user.role === 'coach' ? (
        <div className="coach-dashboard">
          <h1>Dashboard Coach - Benvenuto {user.full_name || user.email}</h1>
          <WorkoutForm />

          {/* Aggiungi altri componenti specifici per coach */}
          <section className="workouts-section">
            <h2>I tuoi workout creati</h2>
            {/* Qui inserire la lista dei workout */}
          </section>
        </div>
      ) : (
        <div className="trainee-dashboard">
          <h1>Dashboard Allievo - Benvenuto {user.full_name || user.email}</h1>

          {/* Aggiungi componenti specifici per allievo */}
          <section className="assigned-workouts">
            <h2>I tuoi workout assegnati</h2>
            {/* Qui inserire la lista dei workout assegnati */}
          </section>
        </div>
      )}
    </AuthGuard>
  );
}