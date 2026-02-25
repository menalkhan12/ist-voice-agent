import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { ProtectedRoute } from './components/ProtectedRoute'
import { DashboardLayout } from './components/DashboardLayout'
import { Login } from './pages/Login'
import { Profile } from './pages/Profile'
import { CallLogs } from './pages/CallLogs'
import { Reports } from './pages/Reports'
import { KnowledgeBase } from './pages/KnowledgeBase'
import { Settings } from './pages/Settings'

export default function App() {
  useEffect(() => {
    const theme = localStorage.getItem('ist_theme')
    if (theme === 'dark') document.documentElement.setAttribute('data-theme', 'dark')
  }, [])

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/profile" replace />} />
        <Route path="profile" element={<Profile />} />
        <Route path="call-logs" element={<CallLogs />} />
        <Route path="reports" element={<Reports />} />
        <Route path="database" element={<KnowledgeBase />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
