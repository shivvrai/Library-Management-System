import { useState, useEffect } from 'react'
import { adminAPI } from '../../utils/api'
import BookManager from './BookManager'
import StudentManagement from './StudentManagement'
import TransactionHistory from './TransactionHistory'
import OverdueBooks from './OverdueBooks'
import './AdminDashboard.css'

const AdminDashboard = ({ onLogout }) => {
  const [activeTab, setActiveTab] = useState('books')
  const [stats, setStats] = useState(null)
  const [books, setBooks] = useState([])
  const [students, setStudents] = useState([])
  const [transactions, setTransactions] = useState([])
  const [overdueBooks, setOverdueBooks] = useState([])

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [statsData, booksData, studentsData, transactionsData, overdueData] = await Promise.all([
        adminAPI.getStats(),
        adminAPI.getBooks(),
        adminAPI.getStudents(),
        adminAPI.getTransactions(),
        adminAPI.getOverdue()
      ])
      
      setStats(statsData)
      setBooks(booksData)
      setStudents(studentsData)
      setTransactions(transactionsData)
      setOverdueBooks(overdueData)
    } catch (err) {
      console.error('Failed to load data:', err)
    }
  }

  return (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <h1>📚 Admin Dashboard</h1>
        <button onClick={onLogout} className="btn btn-secondary">Logout</button>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <h3>{stats.total_books}</h3>
            <p>Total Books</p>
          </div>
          <div className="stat-card">
            <h3>{stats.total_students}</h3>
            <p>Total Students</p>
          </div>
          <div className="stat-card">
            <h3>{stats.active_borrows}</h3>
            <p>Active Borrows</p>
          </div>
          <div className="stat-card">
            <h3>{stats.overdue_books}</h3>
            <p>Overdue Books</p>
          </div>
          <div className="stat-card">
            <h3>₹{stats.total_fines}</h3>
            <p>Total Fines</p>
          </div>
          <div className="stat-card">
            <h3>{stats.total_transactions}</h3>
            <p>Total Transactions</p>
          </div>
        </div>
      )}

      <div className="tabs">
        <button 
          className={activeTab === 'books' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('books')}
        >
          📚 Books
        </button>
        <button 
          className={activeTab === 'students' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('students')}
        >
          👥 Students
        </button>
        <button 
          className={activeTab === 'transactions' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('transactions')}
        >
          📋 Transactions
        </button>
        <button 
          className={activeTab === 'overdue' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('overdue')}
        >
          ⚠️ Overdue
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'books' && <BookManager books={books} onDataChanged={loadData} />}
        {activeTab === 'students' && <StudentManagement />}
        {activeTab === 'transactions' && <TransactionHistory transactions={transactions} onDataChanged={loadData} />}
        {activeTab === 'overdue' && <OverdueBooks overdueBooks={overdueBooks} onDataChanged={loadData} />}
      </div>
    </div>
  )
}

export default AdminDashboard
