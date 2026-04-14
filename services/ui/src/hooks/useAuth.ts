import { useState, useEffect } from 'react'

interface User {
  id: number
  email: string
  display_name: string
  roles: string[]
}

interface AuthState {
  token: string | null
  user: User | null
}

const API_BASE = import.meta.env.VITE_API_URL || '/api'

export function useAuth() {
  const [auth, setAuth] = useState<AuthState>({
    token: localStorage.getItem('phx_token'),
    user: null,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (auth.token && !auth.user) {
      fetchMe(auth.token)
    }
  }, [auth.token])

  async function fetchMe(token: string) {
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) {
        logout()
        return
      }
      const user = await res.json()
      setAuth({ token, user })
    } catch {
      logout()
    }
  }

  async function login(email: string, password: string) {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        setError(data.detail || 'Invalid credentials')
        return false
      }
      const data = await res.json()
      localStorage.setItem('phx_token', data.access_token)
      await fetchMe(data.access_token)
      return true
    } catch (err) {
      setError('Connection failed. Please try again.')
      return false
    } finally {
      setLoading(false)
    }
  }

  function logout() {
    localStorage.removeItem('phx_token')
    setAuth({ token: null, user: null })
  }

  return { auth, login, logout, loading, error }
}
