// /src/utils/api.ts

import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5001', // Backend URL
  headers: {
    'Content-Type': 'application/json',
  },
});

// Optional: Add interceptors if needed
// Example: Handle global errors
api.interceptors.response.use(
  response => response,
  error => {
    // You can handle errors globally here
    return Promise.reject(error);
  }
);

export default api;
