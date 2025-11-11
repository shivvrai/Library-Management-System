// src/utils/api.js
import { getToken } from './auth';

/**
 * Development: use Vite proxy '/api' (forwarded to local backend)
 * Production: use environment variable VITE_API_URL (set it when deploying)
 */
export const API_BASE = import.meta.env.DEV
  ? '/api'
  : (import.meta.env.VITE_API_URL || 'https://library-management-system-aahl.onrender.com/api');

export async function apiCall(endpoint, options = {}) {
  if (!endpoint || typeof endpoint !== 'string') throw new Error('apiCall: endpoint must be a string');

  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${API_BASE}${path}`;

  const token = getToken();

  const providedHeaders = options.headers || {};
  const headers = {
    'Content-Type': 'application/json',
    ...providedHeaders,
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };

  const config = {
    method: options.method || 'GET',
    headers,
    ...(options.body !== undefined
      ? { body: typeof options.body === 'string' ? options.body : JSON.stringify(options.body) }
      : {}),
    ...(['signal', 'credentials', 'mode', 'cache'].reduce((acc, key) => {
      if (options[key] !== undefined) acc[key] = options[key];
      return acc;
    }, {}))
  };

  // Dev logging — OK for development; remove or guard for production
  if (import.meta.env.DEV) {
    console.log(`🔵 API Call: ${config.method} ${path}`, 'hasToken=', !!token);
  }

  try {
    const res = await fetch(url, config);
    const text = await res.text();
    const data = text ? JSON.parse(text) : null;

    if (import.meta.env.DEV) {
      console.log(`📥 Response (${res.status}):`, data);
    }

    if (!res.ok) {
      const errMsg = (data && (data.error || data.message || data.detail)) || `API Error: ${res.status} ${res.statusText}`;
      const err = new Error(errMsg);
      err.status = res.status;
      err.raw = data;
      throw err;
    }

    return data;
  } catch (err) {
    if (err instanceof SyntaxError) {
      throw new Error('Invalid JSON response from server');
    }
    throw err;
  }
}

/* ===== authAPI ===== */
export const authAPI = {
  login: (credentials) => apiCall('/auth/login', { method: 'POST', body: credentials }),
  register: (payload) => apiCall('/auth/register', { method: 'POST', body: payload }),
  checkUsername: (username) => apiCall(`/auth/check-username?username=${encodeURIComponent(username)}`)
};

/* ===== adminAPI ===== */
export const adminAPI = {
  getBooks: () => apiCall('/admin/books'),
  addBook: (book) => apiCall('/admin/books', { method: 'POST', body: book }),
  updateBook: (id, book) => apiCall(`/admin/books/${id}`, { method: 'PUT', body: book }),
  deleteBook: (id) => apiCall(`/admin/books/${id}`, { method: 'DELETE' }),
  getStudents: () => apiCall('/admin/students'),
  addStudent: (payload) => apiCall('/admin/students', { method: 'POST', body: payload }),
  updateStudent: (id, payload) => apiCall(`/admin/students/${id}`, { method: 'PUT', body: payload }),
  deleteStudent: (id) => apiCall(`/admin/students/${id}`, { method: 'DELETE' }),
  getTransactions: () => apiCall('/admin/transactions'),
  getOverdue: () => apiCall('/admin/overdue'),
  processReturn: (transactionId) => apiCall(`/admin/return/${transactionId}`, { method: 'POST' }),
  getStats: () => apiCall('/admin/stats')
};

/* ===== studentAPI ===== */
export const studentAPI = {
  getBooks: () => apiCall('/student/books'),
  getMyBooks: () => apiCall('/student/my-books'),
  getFines: () => apiCall('/student/fines'),
  borrowBook: (bookId) => apiCall('/student/borrow', { method: 'POST', body: { book_id: bookId } }),
  returnBook: (transactionId) => apiCall('/student/return', { method: 'POST', body: { transaction_id: transactionId } })
};

export default { apiCall, authAPI, adminAPI, studentAPI, API_BASE };
