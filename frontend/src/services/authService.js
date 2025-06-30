import api from './api';

export const authService = {
  async login(email, password) {
    // Login con cookie HttpOnly, non gestiamo token manualmente
    const response = await api.post('/auth/login', { email, password }, { withCredentials: true });
    return response.data;
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

  // Metodo isAuthenticated vuoto perché non gestiamo token in frontend
  isAuthenticated() {
    return false;
  }
};
