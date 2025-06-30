import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  withCredentials: true,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
});

// Request Interceptor (logging solo in dev)
api.interceptors.request.use(config => {
  const isDev = process.env.NODE_ENV === 'development';
  const requestId = Math.random().toString(36).substring(2, 6);
  config.metadata = { requestId };

  if (isDev) {
    console.debug(`[API] ${requestId} ${config.method?.toUpperCase()} ${config.url}`, {
      headers: {
        ...config.headers,
        Authorization: config.headers.Authorization ? 'Bearer [HIDDEN]' : undefined
      },
      data: config.data instanceof FormData ? '[FormData]' : config.data
    });
  }

  return config;
});

// Response Interceptor
api.interceptors.response.use(
  response => {
    const { requestId } = response.config.metadata;
    if (process.env.NODE_ENV === 'development') {
      console.debug(`[API] ${requestId} ${response.status}`, {
        path: response.config.url,
        data: response.data
      });
    }
    return response;
  },
  error => {
    if (!error.response) {
      console.error('[API] Network Error:', error.message);
      return Promise.reject({
        code: 'NETWORK_ERROR',
        message: 'Errore di connessione al server',
        isNetworkError: true
      });
    }

    const { status, data } = error.response;
    const { requestId } = error.config?.metadata || {};

    const apiError = {
      status,
      code: data?.code || `HTTP_${status}`,
      message: data?.detail || data?.message || 'Errore nella richiesta API',
      path: error.config?.url,
      timestamp: new Date().toISOString()
    };

    console.error(`[API] ${requestId} Error:`, apiError);
    return Promise.reject(apiError);
  }
);

export default api;
