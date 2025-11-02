import { useState, useEffect } from 'react'
import './App.css'
import Login from './components/Login'
import AdminDashboard from './components/admin/AdminDashboard'
import StudentDashboard from './components/student/StudentDashboard'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [userRole, setUserRole] = useState(null)

  useEffect(() => {
    // Check localStorage directly - no async needed
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr)
        setUserRole(user.role)
        setIsAuthenticated(true)
      } catch (error) {
        console.error('Failed to parse user data:', error)
        localStorage.clear()
      }
    }
  }, [])

  const handleLogin = () => {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        const user = JSON.parse(userStr)
        setUserRole(user.role)
        setIsAuthenticated(true)
      } catch (error) {
        console.error('Failed to parse user data:', error)
      }
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setIsAuthenticated(false)
    setUserRole(null)
  }

  return (
    <div className="app">
      {!isAuthenticated ? (
        <Login onLogin={handleLogin} />
      ) : userRole === 'admin' ? (
        <AdminDashboard onLogout={handleLogout} />
      ) : userRole === 'student' ? (
        <StudentDashboard onLogout={handleLogout} />
      ) : null}
    </div>
  )
}

export default App
