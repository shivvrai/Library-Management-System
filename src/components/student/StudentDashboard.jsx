import { useState, useEffect } from 'react'
import { logout, getUser } from '../../utils/auth'
import { studentAPI } from '../../utils/api'
import { formatDate, calculateDaysRemaining, getDueDateStatus } from '../../utils/dateUtils'
import BrowseBooks from './BrowseBooks'
import MyBooks from './MyBooks'
import './StudentDashboard.css'

const StudentDashboard = ({ onLogout }) => {
  const [availableBooks, setAvailableBooks] = useState([])
  const [myBooks, setMyBooks] = useState([])
  const [fines, setFines] = useState({ fine_amount: 0, borrowed_books: 0 })
  const [activeTab, setActiveTab] = useState('browse')
  const [loading, setLoading] = useState(true)
  const user = getUser()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [books, borrowed, fineData] = await Promise.all([
        studentAPI.getAvailableBooks(),
        studentAPI.getMyBooks(),
        studentAPI.getFines()
      ])
      setAvailableBooks(books)
      setMyBooks(borrowed)
      setFines(fineData)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    onLogout()
  }

  if (loading) {
    return <div className="loading-container">Loading...</div>
  }

  return (
    <div className="student-dashboard">
      <header className="dashboard-header">
        <div>
          <h1>📚 My Library</h1>
          <p>Welcome, {user?.name}!</p>
        </div>
        <button onClick={handleLogout} className="btn logout-btn">Logout</button>
      </header>

      <div className="user-stats">
        <div className="stat-box">
          <span className="label">📚 Books Borrowed:</span>
          <span className="value">{fines.borrowed_books}/3</span>
        </div>
        <div className="stat-box">
          <span className="label">💰 Pending Fines:</span>
          <span className={`value ${fines.fine_amount > 0 ? 'warning' : ''}`}>₹{fines.fine_amount}</span>
        </div>
      </div>

      <nav className="tabs">
        <button className={activeTab === 'browse' ? 'active' : ''} onClick={() => setActiveTab('browse')}>
          🔍 Browse Books
        </button>
        <button className={activeTab === 'my-books' ? 'active' : ''} onClick={() => setActiveTab('my-books')}>
          📖 My Books ({myBooks.length})
        </button>
      </nav>

      <main className="dashboard-content">
        {activeTab === 'browse' && (
          <BrowseBooks books={availableBooks} fines={fines} onBorrow={loadData} />
        )}

        {activeTab === 'my-books' && (
          <MyBooks books={myBooks} onReturn={loadData} />
        )}
      </main>
    </div>
  )
}

export default StudentDashboard
