import { useState, useEffect } from 'react'
import { getToken, logout } from './utils/auth'
import Login from './components/Login'
import AdminDashboard from './components/admin/AdminDashboard'
import StudentDashboard from './components/student/StudentDashboard'
import './App.css'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const token = getToken()
    const storedUser = localStorage.getItem('user')
    
    if (token && storedUser) {
      try {
        setUser(JSON.parse(storedUser))
      } catch (err) {
        logout()
      }
    }
    
    setLoading(false)
  }, [])

  const handleLoginSuccess = (userData) => {
    setUser(userData)
  }

  const handleLogout = () => {
    logout()
    setUser(null)
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div>Loading...</div>
      </div>
    )
  }

  if (!user) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

  return (
    <>
      {user.role === 'admin' && (
        <AdminDashboard user={user} onLogout={handleLogout} />
      )}
      {user.role === 'student' && (
        <StudentDashboard user={user} onLogout={handleLogout} />
      )}
    </>
  )
}

export default App
