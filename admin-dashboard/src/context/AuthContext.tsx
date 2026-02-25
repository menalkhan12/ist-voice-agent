import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { IST_EMAIL_SUFFIX, type User } from '../types'

const STORAGE_TOKEN = 'ist_admin_token'
const STORAGE_USER = 'ist_admin_user'
const DEFAULT_ADMIN_EMAIL = 'admin@ist.edu.pk'
const DEFAULT_ADMIN_PASSWORD = 'admin'

interface AuthState {
  token: string | null
  user: User | null
  isAuthenticated: boolean
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => { success: boolean; error?: string }
  logout: () => void
  updatePassword: (email: string, newPassword: string) => boolean
  getUsers: () => User[]
  addUser: (email: string, password: string, role: User['role']) => { success: boolean; error?: string }
  deleteUser: (email: string) => boolean
  changeUserPassword: (email: string, newPassword: string) => boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

function getStoredUsers(): User[] {
  try {
    const raw = localStorage.getItem('ist_admin_users')
    if (!raw) return [{
      email: DEFAULT_ADMIN_EMAIL,
      role: 'admin',
      password: DEFAULT_ADMIN_PASSWORD,
    }]
    return JSON.parse(raw)
  } catch {
    return [{ email: DEFAULT_ADMIN_EMAIL, role: 'admin', password: DEFAULT_ADMIN_PASSWORD }]
  }
}

function saveUsers(users: User[]) {
  localStorage.setItem('ist_admin_users', JSON.stringify(users))
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    token: localStorage.getItem(STORAGE_TOKEN),
    user: (() => {
      try {
        const u = localStorage.getItem(STORAGE_USER)
        return u ? JSON.parse(u) : null
      } catch {
        return null
      }
    })(),
    isAuthenticated: !!localStorage.getItem(STORAGE_TOKEN),
  })

  const login = useCallback((email: string, password: string) => {
    const trimmed = email.trim().toLowerCase()
    if (!trimmed.endsWith(IST_EMAIL_SUFFIX)) {
      return { success: false, error: 'Only institutional emails ending in @ist.edu.pk are allowed.' }
    }
    const users = getStoredUsers()
    const user = users.find(u => u.email.toLowerCase() === trimmed && u.password === password)
    if (!user) {
      return { success: false, error: 'Invalid email or password.' }
    }
    const token = btoa(JSON.stringify({ email: user.email, at: Date.now() }))
    const safeUser = { email: user.email, role: user.role }
    localStorage.setItem(STORAGE_TOKEN, token)
    localStorage.setItem(STORAGE_USER, JSON.stringify(safeUser))
    setState({ token, user: safeUser, isAuthenticated: true })
    return { success: true }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_TOKEN)
    localStorage.removeItem(STORAGE_USER)
    setState({ token: null, user: null, isAuthenticated: false })
  }, [])

  const updatePassword = useCallback((email: string, newPassword: string): boolean => {
    const users = getStoredUsers()
    const idx = users.findIndex(u => u.email.toLowerCase() === email.toLowerCase())
    if (idx === -1) return false
    users[idx].password = newPassword
    saveUsers(users)
    return true
  }, [])

  const getUsers = useCallback((): User[] => {
    return getStoredUsers().map(u => ({ email: u.email, role: u.role, password: '••••••••' }))
  }, [])

  const addUser = useCallback((email: string, password: string, role: User['role']) => {
    const trimmed = email.trim().toLowerCase()
    if (!trimmed.endsWith(IST_EMAIL_SUFFIX)) {
      return { success: false, error: 'Email must end with @ist.edu.pk' }
    }
    const users = getStoredUsers()
    if (users.some(u => u.email.toLowerCase() === trimmed)) {
      return { success: false, error: 'User already exists.' }
    }
    users.push({ email: trimmed, role, password })
    saveUsers(users)
    return { success: true }
  }, [])

  const deleteUser = useCallback((email: string) => {
    if (email.toLowerCase() === DEFAULT_ADMIN_EMAIL) return false
    const users = getStoredUsers().filter(u => u.email.toLowerCase() !== email.toLowerCase())
    saveUsers(users)
    return true
  }, [])

  const changeUserPassword = useCallback((email: string, newPassword: string) => {
    return updatePassword(email, newPassword)
  }, [updatePassword])

  useEffect(() => {
    const token = localStorage.getItem(STORAGE_TOKEN)
    const userRaw = localStorage.getItem(STORAGE_USER)
    const user = userRaw ? JSON.parse(userRaw) : null
    setState({
      token,
      user,
      isAuthenticated: !!token,
    })
  }, [])

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        logout,
        updatePassword,
        getUsers,
        addUser,
        deleteUser,
        changeUserPassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
