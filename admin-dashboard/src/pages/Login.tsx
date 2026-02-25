import { useState, FormEvent } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { IST_EMAIL_SUFFIX } from '../types'
import './Login.css'

export function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [emailError, setEmailError] = useState('')
  const [submitError, setSubmitError] = useState('')
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  if (isAuthenticated) {
    const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/profile'
    navigate(from, { replace: true })
    return null
  }

  function validateEmail(value: string): boolean {
    const trimmed = value.trim().toLowerCase()
    if (!trimmed) {
      setEmailError('Email is required.')
      return false
    }
    if (!trimmed.endsWith(IST_EMAIL_SUFFIX)) {
      setEmailError('Only institutional emails ending in @ist.edu.pk are allowed.')
      return false
    }
    setEmailError('')
    return true
  }

  function handleEmailBlur() {
    if (email.trim()) validateEmail(email)
  }

  function handleEmailChange(value: string) {
    setEmail(value)
    setSubmitError('')
    if (emailError && value.trim().toLowerCase().endsWith(IST_EMAIL_SUFFIX)) setEmailError('')
    else if (value.trim() && !value.trim().toLowerCase().endsWith(IST_EMAIL_SUFFIX))
      setEmailError('Only institutional emails ending in @ist.edu.pk are allowed.')
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setSubmitError('')
    if (!validateEmail(email)) return
    const result = login(email.trim().toLowerCase(), password)
    if (result.success) {
      const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/profile'
      navigate(from, { replace: true })
    } else {
      setSubmitError(result.error || 'Login failed.')
    }
  }

  return (
    <div className="login-page">
      <div className="login-card card">
        <h1 className="login-title">IST Voice Assistant</h1>
        <p className="login-subtitle">Admin Dashboard</p>
        <form onSubmit={handleSubmit} className="login-form">
          <label className="login-label">Email</label>
          <input
            type="email"
            value={email}
            onChange={e => handleEmailChange(e.target.value)}
            onBlur={handleEmailBlur}
            className={`login-input ${emailError ? 'invalid' : ''}`}
            placeholder="you@ist.edu.pk"
            autoComplete="username"
          />
          {emailError && <p className="input-error">{emailError}</p>}
          <label className="login-label">Password</label>
          <input
            type="password"
            value={password}
            onChange={e => { setPassword(e.target.value); setSubmitError('') }}
            className="login-input"
            placeholder="••••••••"
            autoComplete="current-password"
          />
          {submitError && <p className="input-error">{submitError}</p>}
          <button type="submit" className="btn btn-primary login-submit">
            Sign in
          </button>
        </form>
        <p className="login-hint">Default: admin@ist.edu.pk / admin</p>
      </div>
    </div>
  )
}
