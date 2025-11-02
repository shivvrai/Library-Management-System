import { useState } from 'react'
import { adminAPI } from '../../utils/api'

const BookManager = ({ books, onDataChanged }) => {
  const [showForm, setShowForm] = useState(false)
  const [newBook, setNewBook] = useState({
    title: '',
    author: '',
    pages: '',
    price: '',
    isbn: '',
    category: '',
    quantity: '1'
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const categories = [
    'Fiction', 'Non-Fiction', 'Science', 'Technology', 'History',
    'Biography', 'Fantasy', 'Romance', 'Mystery', 'Thriller'
  ]

  const validateISBN = (isbn) => {
  const cleanISBN = isbn.replace(/[-\s]/g, '')
  return cleanISBN.length === 13 && /^\d{13}$/.test(cleanISBN)
}

const validateForm = () => {
  const newErrors = {}

  if (!newBook.title.trim()) newErrors.title = 'Title is required'
  if (!newBook.author.trim()) newErrors.author = 'Author is required'
  if (!newBook.pages || parseInt(newBook.pages) <= 0) newErrors.pages = 'Valid page count is required'
  if (!newBook.price || parseFloat(newBook.price) <= 0) newErrors.price = 'Valid price is required'
  if (!newBook.quantity || parseInt(newBook.quantity) <= 0) newErrors.quantity = 'Valid quantity is required'
  if (!newBook.isbn.trim()) newErrors.isbn = 'ISBN is required'
  else if (!validateISBN(newBook.isbn)) newErrors.isbn = 'Invalid ISBN-13 format'
  if (!newBook.category.trim()) newErrors.category = 'Category is required'

  setErrors(newErrors)
  return Object.keys(newErrors).length === 0
}


  const addBook = async () => {
  if (!validateForm()) return
  
  const bookToAdd = {
    ...newBook,
    pages: parseInt(newBook.pages),
    price: parseFloat(newBook.price),
    quantity: parseInt(newBook.quantity)
  }
  
  console.log('📚 Sending book data:', bookToAdd) // DEBUG: See what's being sent
  
  setLoading(true)
  try {
    const response = await adminAPI.addBook(bookToAdd)
    
    setNewBook({
      title: '',
      author: '',
      pages: '',
      price: '',
      isbn: '',
      category: '',
      quantity: '1'
    })
    setErrors({})
    setShowForm(false)
    alert('Book added successfully!')
    onDataChanged()
  } catch (err) {
    console.error('❌ Full error:', err) // DEBUG: See full error
    
    // Extract actual error message from backend
    let errorMessage = 'Failed to add book'
    
    if (err.message) {
      errorMessage = err.message
    }
    
    // Show error in UI
    setErrors({ general: errorMessage })
    alert(`❌ Error: ${errorMessage}`)
  } finally {
    setLoading(false)
  }
}



  const deleteBook = async (id) => {
    if (!window.confirm('Delete this book?')) return
    try {
      await adminAPI.deleteBook(id)
      onDataChanged()
    } catch (err) {
      alert('Failed to delete book')
    }
  }

  return (
    <div className="book-manager">
      <div className="manager-header">
        <h2>Books Management</h2>
        <button onClick={() => setShowForm(!showForm)} className="btn btn-primary">
          {showForm ? '✕ Close' : '+ Add Book'}
        </button>
      </div>

      {showForm && (
        <div className="form-container">
          <div className="form-row">
            <div className="form-group">
              <label>Title *</label>
              <input type="text" placeholder="Book title" value={newBook.title} onChange={(e) => setNewBook({...newBook, title: e.target.value})} />
              {errors.title && <span className="error">{errors.title}</span>}
            </div>
            <div className="form-group">
              <label>Author *</label>
              <input type="text" placeholder="Author name" value={newBook.author} onChange={(e) => setNewBook({...newBook, author: e.target.value})} />
              {errors.author && <span className="error">{errors.author}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Pages *</label>
              <input type="number" placeholder="Pages" value={newBook.pages} onChange={(e) => setNewBook({...newBook, pages: e.target.value})} />
              {errors.pages && <span className="error">{errors.pages}</span>}
            </div>
            <div className="form-group">
              <label>Price ($) *</label>
              <input type="number" step="0.01" placeholder="Price" value={newBook.price} onChange={(e) => setNewBook({...newBook, price: e.target.value})} />
              {errors.price && <span className="error">{errors.price}</span>}
            </div>
            <div className="form-group">
              <label>Quantity *</label>
              <input type="number" placeholder="Quantity" value={newBook.quantity} onChange={(e) => setNewBook({...newBook, quantity: e.target.value})} />
              {errors.quantity && <span className="error">{errors.quantity}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>ISBN (13) *</label>
              <input type="text" placeholder="ISBN" value={newBook.isbn} onChange={(e) => setNewBook({...newBook, isbn: e.target.value})} />
              {errors.isbn && <span className="error">{errors.isbn}</span>}
            </div>
            <div className="form-group">
              <label>Category *</label>
              <select value={newBook.category} onChange={(e) => setNewBook({...newBook, category: e.target.value})}>
                <option value="">Select Category</option>
                {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
              </select>
              {errors.category && <span className="error">{errors.category}</span>}
            </div>
          </div>

          {errors.general && <div className="error-message">❌ {errors.general}</div>}

          <div className="form-actions">
            <button onClick={addBook} disabled={loading} className="btn btn-success">
              {loading ? 'Adding...' : '✓ Add Book'}
            </button>
            <button onClick={() => setShowForm(false)} className="btn btn-secondary">Cancel</button>
          </div>
        </div>
      )}

      <div className="books-grid">
        {books.map(book => (
          <div key={book.id} className="book-card">
            <h3>{book.title}</h3>
            <p className="author">{book.author}</p>
            <p className="meta">Pages: {book.pages} | Price: ${book.price}</p>
            <p className="meta">ISBN: {book.isbn}</p>
            <p className="category">Category: {book.category}</p>
            <p className="availability">Available: {book.available}/{book.quantity}</p>
            <button onClick={() => deleteBook(book.id)} className="btn btn-danger">🗑️ Delete</button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default BookManager
