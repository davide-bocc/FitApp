import api from './api';

export const authService = {
  async getProtectedData() {
    try {
      // Invia SOLO il cookie, senza header Authorization
      const response = await api.post('/coaches/coaches/workouts/',
        { /* dati della richiesta */ },
        {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error:', error);
      throw error;
    }
  },

  async login(email, password) {
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const response = await api.post('/auth/login', formData, {
        withCredentials: true,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Login failed:', error.response?.data || error.message);
      throw error;
    }
  },

  async logout() {
    try {
      await api.post('/auth/logout', {}, { withCredentials: true });
    } catch (error) {
      console.error('Errore durante logout:', error.message);
    }
  },

  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me', { withCredentials: true });
      return response.data;
    } catch (error) {
      console.error('Errore getCurrentUser:', error);
      return null;
    }

  },

  isAuthenticated() {
    return false;
  }
};
