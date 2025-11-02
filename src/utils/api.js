import { getToken } from './auth'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'
const DEV_MODE = false

const mockBooks = [
  {id: 1, title: "The Lord of the Rings", author: "J.R.R. Tolkien", pages: 1178, price: 25.50, isbn: "9780618053267", category: "Fantasy", quantity: 5, available: 5},
  {id: 2, title: "The Hobbit", author: "J.R.R. Tolkien", pages: 310, price: 15.00, isbn: "9780345339683", category: "Fantasy", quantity: 8, available: 8},
  {id: 3, title: "Pride and Prejudice", author: "Jane Austen", pages: 279, price: 12.75, isbn: "9780141439518", category: "Romance", quantity: 3, available: 3},
  {id: 4, title: "1984", author: "George Orwell", pages: 328, price: 10.20, isbn: "9780451524935", category: "Fiction", quantity: 4, available: 4},
]

const mockStudents = [
  {username: 'student1', id: 'S001', name: 'Rahul Kumar', email: 'rahul@example.com', phone: '9876543210', borrowed_books: 0, fine_amount: 0},
  {username: 'student2', id: 'S002', name: 'Priya Sharma', email: 'priya@example.com', phone: '9876543211', borrowed_books: 0, fine_amount: 0},
]

const mockTransactions = []

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

  console.log(`🔵 API Call: ${options.method || 'GET'} ${url}`) // DEBUG

  try {
    const response = await fetch(url, config)
    
    // Parse response body first
    const data = await response.json()
    
    console.log(`📥 Response (${response.status}):`, data) // DEBUG: See response
    
    // If response not OK, throw with backend error message
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



function mockApiCall(endpoint, options) {
  return new Promise((resolve) => {
    setTimeout(() => {
      if (endpoint === '/admin/books') resolve(mockBooks)
      else if (endpoint === '/admin/students') resolve(mockStudents)
      else if (endpoint === '/admin/transactions') resolve(mockTransactions)
      else if (endpoint === '/admin/overdue') resolve([])
      else if (endpoint === '/admin/stats') resolve({
        total_books: mockBooks.length,
        total_students: mockStudents.length,
        active_borrows: 0,
        overdue_books: 0,
        total_fines: 0,
        total_transactions: 0
      })
      else if (endpoint === '/student/books/available') resolve(mockBooks)
      else if (endpoint === '/student/my-books') resolve([])
      else if (endpoint === '/student/fines') resolve({fine_amount: 0, borrowed_books: 0})
      else resolve({success: true})
    }, 300)
  })
}

export const adminAPI = {
  getBooks: () => apiCall('/admin/books'),
  addBook: async (bookData) => {
    const response = await apiCall('/admin/books', {
      method: 'POST',
      body: JSON.stringify(bookData)
    })
    
    // If response has error, throw it
    if (response.error) {
      throw new Error(response.error)
    }
    
    return response
  },
  
  updateBook: (id, book) => apiCall(`/admin/books/${id}`, { method: 'PUT', body: JSON.stringify(book) }),
  deleteBook: (id) => apiCall(`/admin/books/${id}`, { method: 'DELETE' }),
  getStudents: () => apiCall('/admin/students'),
  getTransactions: () => apiCall('/admin/transactions'),
  getOverdue: () => apiCall('/admin/overdue'),
  processReturn: (transactionId) => apiCall(`/admin/return/${transactionId}`, { method: 'POST' }),
  getStats: () => apiCall('/admin/stats'),
}

export const studentAPI = {
  getAvailableBooks: () => apiCall('/student/books/available'),
  borrowBook: (bookId) => apiCall('/student/borrow', { method: 'POST', body: JSON.stringify({ book_id: bookId }) }),
  getMyBooks: () => apiCall('/student/my-books'),
  returnBook: (transactionId) => apiCall(`/student/return/${transactionId}`, { method: 'POST' }),
  getFines: () => apiCall('/student/fines'),
}
