import api from './services/api';

const testAuthFlow = async () => {
  // 1. Login
  const loginRes = await api.post('/auth/login', new URLSearchParams({
    username: 'davide.bocc@gmail.com',
    password: 'Prova1234!'
  }));

  console.log('Login OK - Token:', loginRes.data.access_token);

  // 2. Verifica token
  const meRes = await api.get('/auth/me');
  console.log('Dati utente:', meRes.data);

  // 3. Crea workout
  const workoutRes = await api.post('/coaches/workouts/', {
    name: "Test Debug",
    description: "Creato da frontend"
  });
  console.log('Workout creato:', workoutRes.data);
};

testAuthFlow().catch(err => {
  console.error('Test fallito:', {
    status: err.response?.status,
    headers: err.config?.headers,
    data: err.response?.data
  });
});