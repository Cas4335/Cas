import React from 'react'
import { useAuth } from './hooks/useAuth'
import LoginPage from './pages/LoginPage'
import ChatPage from './pages/ChatPage'

export default function App() {
  const { auth, login, logout, loading, error } = useAuth()

  if (!auth.token || !auth.user) {
    return <LoginPage onLogin={login} loading={loading} error={error} />
  }

  return (
    <ChatPage
      token={auth.token}
      userName={auth.user.display_name}
      roles={auth.user.roles}
      onLogout={logout}
    />
  )
}
