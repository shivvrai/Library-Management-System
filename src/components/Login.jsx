import { useState } from 'react'
import { authAPI } from '../utils/api'
import StudentRegister from './StudentRegister'
import './Login.css'

const Login = ({ onLoginSuccess }) => {
  const [showRegister, setShowRegister] = useState(false)
  const [credentials, setCredentials] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setCredentials(prev => ({ ...prev, [name]: value }))
    setError('')
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    
    if (!credentials.username || !credentials.password) {
      setError('Username and password are required')
      return
    }

    setLoading(true)
    try {
      const response = await authAPI.login(credentials)
      
      // Store token
      localStorage.setItem('token', response.token)
      localStorage.setItem('user', JSON.stringify(response.user))
      
      onLoginSuccess(response.user)
    } catch (err) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  if (showRegister) {
    return <StudentRegister onSuccess={() => {
      setShowRegister(false)
      setCredentials({ username: '', password: '' })
    }} onBackToLogin={() => setShowRegister(false)} />
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>📚 Library System</h1>
          <p>Student & Admin Portal</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              name="username"
              value={credentials.username}
              onChange={handleInputChange}
              placeholder="Enter username"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={credentials.password}
              onChange={handleInputChange}
              placeholder="Enter password"
              disabled={loading}
            />
          </div>

          <button type="submit" disabled={loading} className="btn btn-primary btn-login">
            {loading ? 'Logging in...' : '🔓 Login'}
          </button>
        </form>

        <div className="divider">OR</div>

        <button 
          onClick={() => setShowRegister(true)} 
          className="btn btn-secondary btn-register"
        >
          📝 Create Student Account
        </button>

        <div className="login-footer">
          <p><strong>Demo Credentials:</strong></p>
          <p><small>Admin: admin / admin123</small></p>
          <p><small>Student: rahul.kumar / pass123</small></p>
        </div>
      </div>
    </div>
  )
}

export default Login
