import axios from 'axios';

const api = axios.create({
  baseURL: '/api',  // This will use the proxy configured in vite.config.ts
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  console.log('🔍 Making API request to:', config.url);
  const token = localStorage.getItem('token');
  console.log('🔑 Token found:', token ? 'Yes' : 'No');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log('📨 Request headers:', config.headers);
  } else {
    console.warn('⚠️ No token found in localStorage');
  }
  return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('❌ API Error:', {
      status: error.response?.status,
      data: error.response?.data,
      config: error.config
    });
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      localStorage.removeItem('userId');  // Clean up old storage
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api; 