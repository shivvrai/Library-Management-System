// TEMPORARY: Bypass authentication for Vercel deployment
const DEV_MODE = true // Set to false when backend is deployed

const API_BASE = 'http://localhost:5000/api'

export const login = async (username, password) => {
  // TEMPORARY BYPASS: Auto-login without backend
  if (DEV_MODE) {
    console.log('DEV MODE: Auto-login enabled')
    localStorage.setItem('token', 'dev-token-bypass')
    localStorage.setItem('user', JSON.stringify({
      username: username || 'admin',
      role: 'admin',
      name: 'Admin User'
    }))
    return true
  }

  // Real authentication (will work when DEV_MODE = false)
  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password })
    })

    if (response.ok) {
      const data = await response.json()
      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))
      return true
    }
    return false
  } catch (error) {
    console.error('Login error:', error)
    return false
  }
}

export const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

export const checkAuthStatus = async () => {
  // TEMPORARY BYPASS: Always return true
  if (DEV_MODE) {
    return localStorage.getItem('token') !== null
  }

  const token = localStorage.getItem('token')
  if (!token) return false

  try {
    const response = await fetch(`${API_BASE}/auth/verify`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    return response.ok
  } catch (error) {
    console.error('Auth check error:', error)
    return false
  }
}

export const getToken = () => {
  return localStorage.getItem('token')
}

export const getUser = () => {
  const user = localStorage.getItem('user')
  return user ? JSON.parse(user) : null
}

// const API_BASE = 'http://localhost:5000/api'

// export const login = async (username, password) => {
//   try {
//     const response = await fetch(`${API_BASE}/auth/login`, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json'
//       },
//       body: JSON.stringify({ username, password })
//     })

//     if (response.ok) {
//       const data = await response.json()
//       localStorage.setItem('token', data.token)
//       localStorage.setItem('user', JSON.stringify(data.user))
//       return true
//     }
//     return false
//   } catch (error) {
//     console.error('Login error:', error)
//     return false
//   }
// }

// export const logout = () => {
//   localStorage.removeItem('token')
//   localStorage.removeItem('user')
// }

// export const checkAuthStatus = async () => {
//   const token = localStorage.getItem('token')
//   if (!token) return false

//   try {
//     const response = await fetch(`${API_BASE}/auth/verify`, {
//       headers: {
//         'Authorization': `Bearer ${token}`
//       }
//     })
//     return response.ok
//   } catch (error) {
//     console.error('Auth check error:', error)
//     return false
//   }
// }

// export const getToken = () => {
//   return localStorage.getItem('token')
// }

// export const getUser = () => {
//   const user = localStorage.getItem('user')
//   return user ? JSON.parse(user) : null
// }
