import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  transformRequest: [(data, headers) => {
    // Gestione automatica di URLSearchParams
    if (data instanceof URLSearchParams) {
      headers['Content-Type'] = 'application/x-www-form-urlencoded';
      return data.toString();
    }
    return data;
  }]
});

// Interceptor
api.interceptors.request.use(config => {
  if (config.data instanceof FormData) {
    config.headers['Content-Type'] = 'multipart/form-data';

    // Debug: mostra il contenuto di FormData
    const formDataObj = {};
    config.data.forEach((value, key) => formDataObj[key] = value);
    console.log('Interceptor - FormData:', formDataObj);
  }
  return config;
});

export default api;

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log('[API] Response from:', response.config.url);
    return response;
  },
  (error) => {
    const errorData = {
      status: error.response?.status,
      message: error.response?.data?.detail || error.message,
      url: error.config?.url
    };
    console.error('[API] Error:', errorData);

    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      sessionStorage.removeItem('authToken');
      window.location.href = '/auth/login';
    }

    return Promise.reject(errorData);
  }
);

export default api;