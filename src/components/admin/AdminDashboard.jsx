import { useState, useEffect } from 'react'
import { adminAPI } from '../../utils/api'
import { logout } from '../../utils/auth'
import BookManager from './BookManager'
import StudentManager from './StudentManager'
import TransactionHistory from './TransactionHistory'
import OverdueBooks from './OverdueBooks'
import './AdminDashboard.css'

export default function AdminDashboard({ onLogout }) {
  const [activeTab, setActiveTab] = useState('overview')
  const [stats, setStats] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      const data = await adminAPI.getStats()
      setStats(data)
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    if (onLogout) onLogout()
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>📚 Admin Dashboard</h1>
        <button className="btn btn-secondary" onClick={handleLogout}>
          Logout
        </button>
      </header>

      <nav className="dashboard-nav">
        <button 
          className={`nav-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`nav-btn ${activeTab === 'books' ? 'active' : ''}`}
          onClick={() => setActiveTab('books')}
        >
          Books
        </button>
        <button 
          className={`nav-btn ${activeTab === 'students' ? 'active' : ''}`}
          onClick={() => setActiveTab('students')}
        >
          Students
        </button>
        <button 
          className={`nav-btn ${activeTab === 'transactions' ? 'active' : ''}`}
          onClick={() => setActiveTab('transactions')}
        >
          Transactions
        </button>
        <button 
          className={`nav-btn ${activeTab === 'overdue' ? 'active' : ''}`}
          onClick={() => setActiveTab('overdue')}
        >
          Overdue
        </button>
      </nav>

      <main className="dashboard-content">
        {activeTab === 'overview' && (
          <div className="overview-section">
            <h2>Library Statistics</h2>
            {loading ? (
              <div className="loading">Loading statistics...</div>
            ) : (
              <div className="stats-grid">
                <div className="stat-card">
                  <h3>Total Books</h3>
                  <p className="stat-value">{stats.total_books || 0}</p>
                </div>
                <div className="stat-card">
                  <h3>Total Students</h3>
                  <p className="stat-value">{stats.total_students || 0}</p>
                </div>
                <div className="stat-card">
                  <h3>Active Borrows</h3>
                  <p className="stat-value">{stats.active_borrows || 0}</p>
                </div>
                <div className="stat-card">
                  <h3>Overdue Books</h3>
                  <p className="stat-value">{stats.overdue_books || 0}</p>
                </div>
                <div className="stat-card">
                  <h3>Total Fines</h3>
                  <p className="stat-value">₹{stats.total_fines || 0}</p>
                </div>
                <div className="stat-card">
                  <h3>Total Transactions</h3>
                  <p className="stat-value">{stats.total_transactions || 0}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'books' && (
          <BookManager books={[]} onDataChanged={loadStats} />
        )}

        {activeTab === 'students' && (
          <StudentManager students={[]} />
        )}

        {activeTab === 'transactions' && <TransactionHistory />}

        {activeTab === 'overdue' && <OverdueBooks />}
      </main>
    </div>
  )
}
