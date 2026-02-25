import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { IST_EMAIL_SUFFIX } from '../types'
import './Settings.css'

export function Settings() {
  const { user, getUsers, addUser, deleteUser, changeUserPassword } = useAuth()
  const isAdmin = user?.email?.toLowerCase() === 'admin@ist.edu.pk'
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    if (typeof document !== 'undefined' && document.documentElement.getAttribute('data-theme') === 'dark') return 'dark'
    return 'light'
  })
  const [addEmail, setAddEmail] = useState('')
  const [addPassword, setAddPassword] = useState('')
  const [addError, setAddError] = useState('')
  const [addSuccess, setAddSuccess] = useState(false)
  const [changePassEmail, setChangePassEmail] = useState('')
  const [changePassNew, setChangePassNew] = useState('')
  const [changePassMessage, setChangePassMessage] = useState('')
  const [users, setUsers] = useState(getUsers())

  function handleToggleTheme() {
    const next = theme === 'light' ? 'dark' : 'light'
    setTheme(next)
    document.documentElement.setAttribute('data-theme', next)
    localStorage.setItem('ist_theme', next)
  }

  function handleAddUser(e: React.FormEvent) {
    e.preventDefault()
    setAddError('')
    setAddSuccess(false)
    if (!addEmail.trim().toLowerCase().endsWith(IST_EMAIL_SUFFIX)) {
      setAddError('Email must end with @ist.edu.pk')
      return
    }
    const result = addUser(addEmail.trim().toLowerCase(), addPassword, 'user')
    if (result.success) {
      setAddEmail('')
      setAddPassword('')
      setAddSuccess(true)
      setUsers(getUsers())
    } else {
      setAddError(result.error || 'Failed to add user')
    }
  }

  function handleDeleteUser(email: string) {
    if (!confirm(`Remove user ${email}?`)) return
    if (deleteUser(email)) setUsers(getUsers())
  }

  function handleChangeUserPassword(e: React.FormEvent) {
    e.preventDefault()
    setChangePassMessage('')
    if (!changePassEmail.trim() || !changePassNew.trim()) {
      setChangePassMessage('Email and new password required.')
      return
    }
    if (changeUserPassword(changePassEmail.trim().toLowerCase(), changePassNew)) {
      setChangePassMessage('Password updated.')
      setChangePassEmail('')
      setChangePassNew('')
    } else {
      setChangePassMessage('User not found or update failed.')
    }
  }

  return (
    <div className="settings-page">
      <h2 className="page-heading">Settings</h2>

      {isAdmin && (
        <>
          <div className="card">
            <h3 className="card-title">User management</h3>
            <form onSubmit={handleAddUser} className="settings-form">
              <label>Add user (email must end with @ist.edu.pk)</label>
              <div className="settings-row">
                <input
                  type="email"
                  value={addEmail}
                  onChange={e => { setAddEmail(e.target.value); setAddError('') }}
                  placeholder="name@ist.edu.pk"
                  className="settings-input"
                />
                <input
                  type="password"
                  value={addPassword}
                  onChange={e => setAddPassword(e.target.value)}
                  placeholder="Password"
                  className="settings-input"
                />
                <button type="submit" className="btn btn-primary">Add User</button>
              </div>
              {addError && <p className="input-error">{addError}</p>}
              {addSuccess && <p className="settings-success">User added.</p>}
            </form>
            <form onSubmit={handleChangeUserPassword} className="settings-form" style={{ marginTop: 20 }}>
              <label>Change user password</label>
              <div className="settings-row">
                <input
                  type="email"
                  value={changePassEmail}
                  onChange={e => setChangePassEmail(e.target.value)}
                  placeholder="user@ist.edu.pk"
                  className="settings-input"
                />
                <input
                  type="password"
                  value={changePassNew}
                  onChange={e => setChangePassNew(e.target.value)}
                  placeholder="New password"
                  className="settings-input"
                />
                <button type="submit" className="btn btn-outline">Change Password</button>
              </div>
              {changePassMessage && <p className={changePassMessage === 'Password updated.' ? 'settings-success' : 'input-error'}>{changePassMessage}</p>}
            </form>
            <h4 style={{ marginTop: 24, marginBottom: 12 }}>Users</h4>
            <ul className="settings-user-list">
              {users.map(u => (
                <li key={u.email}>
                  <span>{u.email}</span>
                  <span>{u.role}</span>
                  {u.email.toLowerCase() !== 'admin@ist.edu.pk' && (
                    <button type="button" className="btn btn-outline btn-sm btn-danger" onClick={() => handleDeleteUser(u.email)}>Delete</button>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </>
      )}

      <div className="card">
        <h3 className="card-title">Appearance</h3>
        <div className="settings-row settings-toggle">
          <span>Theme</span>
          <button type="button" className="btn btn-outline" onClick={handleToggleTheme}>
            {theme === 'light' ? 'Dark' : 'Light'} mode
          </button>
        </div>
      </div>

      <div className="card">
        <h3 className="card-title">System</h3>
        <div className="settings-row">
          <button type="button" className="btn btn-outline">Backup Data</button>
          <button type="button" className="btn btn-outline">Restore Defaults</button>
        </div>
        <p className="settings-hint">Backend integration will enable full backup and restore.</p>
      </div>
    </div>
  )
}
