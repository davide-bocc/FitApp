import { useEffect, useState } from 'react';
import api from '../../services/api';

export default function WorkoutList() {
  const [workouts, setWorkouts] = useState([]);

  useEffect(() => {
    const fetchWorkouts = async () => {
      try {
        const response = await api.get('/coaches/workouts/');
        setWorkouts(response.data);
      } catch (error) {
        console.error('Errore nel caricamento workout:', error);
      }
    };
    fetchWorkouts();
  }, []);

  return (
    <ul>
      {workouts.map(workout => (
        <li key={workout.id}>
          <h3>{workout.title}</h3>
          <p>Esercizi: {workout.exercises.length}</p>
        </li>
      ))}
    </ul>
  );
}