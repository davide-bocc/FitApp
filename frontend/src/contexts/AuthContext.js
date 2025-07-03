import { createContext, useContext, useState, useEffect } from 'react';
import { login as authLogin, getCurrentUser, logout as authLogout } from '../services/authService';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUser = async () => {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
      } catch (err) {
        console.error('Failed to load user:', err);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    loadUser();
  }, []);

  const login = async (email, password) => {
  const response = await api.post('/auth/login', {
    username: email,
    password
  }, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'  // Formato corretto per OAuth2
    }
  });

  // Non memorizzare il token in localStorage - usa solo il cookie HttpOnly
  return response.data.user;
 };

 const fetchProtectedData = async () => {
   return await api.get('/protected-route');
   // Axios gestirà automaticamente i cookie
 };

  const logout = async () => {
    try {
      await authLogout();
    } finally {
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      logout,
      isAuthenticated: !!user && !loading
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};