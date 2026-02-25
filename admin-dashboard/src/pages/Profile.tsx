import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import './Profile.css'

export function Profile() {
  const { user, updatePassword } = useAuth()
  const [showChangePassword, setShowChangePassword] = useState(false)
  const [showLoginHistory, setShowLoginHistory] = useState(false)
  const [passwordForm, setPasswordForm] = useState({ current: '', new: '', confirm: '' })
  const [passwordMessage, setPasswordMessage] = useState('')

  const roleDisplay = user?.email?.toLowerCase() === 'admin@ist.edu.pk' ? 'Administrator' : 'Institutional User'

  function handleChangePassword(e: React.FormEvent) {
    e.preventDefault()
    setPasswordMessage('')
    if (passwordForm.new !== passwordForm.confirm) {
      setPasswordMessage('New passwords do not match.')
      return
    }
    if (passwordForm.new.length < 4) {
      setPasswordMessage('Password must be at least 4 characters.')
      return
    }
    if (!user?.email) return
    const ok = updatePassword(user.email, passwordForm.new)
    if (ok) {
      setPasswordMessage('Password updated successfully.')
      setPasswordForm({ current: '', new: '', confirm: '' })
      setShowChangePassword(false)
    } else {
      setPasswordMessage('Failed to update password.')
    }
  }

  const loginHistory = (() => {
    try {
      const raw = localStorage.getItem('ist_login_history')
      return raw ? JSON.parse(raw) : []
    } catch {
      return []
    }
  })()

  return (
    <div className="profile-page">
      <h2 className="page-heading">User Profile</h2>
      <div className="card profile-card">
        <h3 className="card-title">Account Information</h3>
        <dl className="profile-dl">
          <dt>Email</dt>
          <dd>{user?.email ?? '—'}</dd>
          <dt>Role</dt>
          <dd>{roleDisplay}</dd>
        </dl>
        <div className="profile-actions">
          <button type="button" className="btn btn-outline" onClick={() => setShowChangePassword(false)}>
            Edit Profile
          </button>
          <button type="button" className="btn btn-primary" onClick={() => setShowChangePassword(true)}>
            Change Password
          </button>
          <button type="button" className="btn btn-outline" onClick={() => setShowLoginHistory(true)}>
            View Login History
          </button>
        </div>
      </div>

      {showChangePassword && (
        <div className="card">
          <h3 className="card-title">Change Password</h3>
          <form onSubmit={handleChangePassword} className="profile-form">
            <label>Current password</label>
            <input
              type="password"
              value={passwordForm.current}
              onChange={e => setPasswordForm(p => ({ ...p, current: e.target.value }))}
              className="profile-input"
            />
            <label>New password</label>
            <input
              type="password"
              value={passwordForm.new}
              onChange={e => setPasswordForm(p => ({ ...p, new: e.target.value }))}
              className="profile-input"
            />
            <label>Confirm new password</label>
            <input
              type="password"
              value={passwordForm.confirm}
              onChange={e => setPasswordForm(p => ({ ...p, confirm: e.target.value }))}
              className="profile-input"
            />
            {passwordMessage && <p className={passwordMessage.startsWith('Password updated') ? 'profile-msg success' : 'input-error'}>{passwordMessage}</p>}
            <div className="profile-form-actions">
              <button type="button" className="btn btn-outline" onClick={() => setShowChangePassword(false)}>Cancel</button>
              <button type="submit" className="btn btn-primary">Save Password</button>
            </div>
          </form>
        </div>
      )}

      {showLoginHistory && (
        <div className="card">
          <h3 className="card-title">Login History</h3>
          <div className="login-history-list">
            {loginHistory.length === 0 ? (
              <p className="text-secondary">No login history recorded yet.</p>
            ) : (
              <ul>
                {loginHistory.slice(0, 20).map((entry: { email: string; timestamp: string }, i: number) => (
                  <li key={i}>{entry.email} — {new Date(entry.timestamp).toLocaleString()}</li>
                ))}
              </ul>
            )}
          </div>
          <button type="button" className="btn btn-outline" onClick={() => setShowLoginHistory(false)}>Close</button>
        </div>
      )}
    </div>
  )
}
