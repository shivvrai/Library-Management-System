import { getToken } from './auth'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`
  const token = getToken()

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    },
    ...options
  }

  console.log(`🔵 API Call: ${options.method || 'GET'} ${url}`)

  try {
    const response = await fetch(url, config)
    const data = await response.json()
    
    console.log(`📥 Response (${response.status}):`, data)
    
    if (!response.ok) {
      const errorMsg = data.error || data.message || `API Error: ${response.status}`
      throw new Error(errorMsg)
    }
    
    return data
  } catch (error) {
    console.error('❌ API call failed:', error)
    throw error
  }
}

// Auth API
export const authAPI = {
  login: (credentials) => apiCall('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials)
  }),
  
  register: (studentData) => apiCall('/auth/register', {
    method: 'POST',
    body: JSON.stringify(studentData)
  }),
  
  checkUsername: (username) => apiCall(`/auth/check-username?username=${encodeURIComponent(username)}`),
  
  suggestUsernames: (name) => apiCall(`/auth/suggest-usernames?name=${encodeURIComponent(name)}`)
}

// Admin API
export const adminAPI = {
  // Books Management
  getBooks: () => apiCall('/admin/books'),
  
  addBook: (bookData) => apiCall('/admin/books', {
    method: 'POST',
    body: JSON.stringify(bookData)
  }),
  
  updateBook: (id, book) => apiCall(`/admin/books/${id}`, {
    method: 'PUT',
    body: JSON.stringify(book)
  }),
  
  deleteBook: (id) => apiCall(`/admin/books/${id}`, {
    method: 'DELETE'
  }),
  
  updateQuantity: (id, action, amount = 1) => apiCall(`/admin/books/${id}/quantity`, {
    method: 'PATCH',
    body: JSON.stringify({ action, amount })
  }),
  
  searchBooks: (query) => apiCall(`/admin/books/search?q=${encodeURIComponent(query || '')}`),
  
  // Student Management
  getStudents: () => apiCall('/admin/students'),
  
  addStudent: (studentData) => apiCall('/admin/students', {
    method: 'POST',
    body: JSON.stringify(studentData)
  }),
  
  updateStudent: (id, studentData) => apiCall(`/admin/students/${id}`, {
    method: 'PUT',
    body: JSON.stringify(studentData)
  }),
  
  deleteStudent: (id) => apiCall(`/admin/students/${id}`, {
    method: 'DELETE'
  }),
  
  searchStudents: (query) => apiCall(`/admin/students/search?q=${encodeURIComponent(query || '')}`),
  
  // Transactions & Stats
  getTransactions: () => apiCall('/admin/transactions'),
  getOverdue: () => apiCall('/admin/overdue'),
  processReturn: (transactionId) => apiCall(`/admin/return/${transactionId}`, {
    method: 'POST'
  }),
  getStats: () => apiCall('/admin/stats')
}

// Student API
export const studentAPI = {
  getAvailableBooks: () => apiCall('/student/books/available'),
  
  searchBooks: (query) => apiCall(`/student/books/search?q=${encodeURIComponent(query || '')}`),
  
  borrowBook: (bookId) => apiCall('/student/borrow', {
    method: 'POST',
    body: JSON.stringify({ book_id: bookId })
  }),
  
  getMyBooks: () => apiCall('/student/my-books'),
  
  returnBook: (transactionId) => apiCall(`/student/return/${transactionId}`, {
    method: 'POST'
  }),
  
  getFines: () => apiCall('/student/fines')
}
