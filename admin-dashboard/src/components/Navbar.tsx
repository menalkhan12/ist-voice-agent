import { useAuth } from '../context/AuthContext'
import './Navbar.css'

interface NavbarProps {
  onToggleSidebar: () => void
  sidebarCollapsed: boolean
}

export function Navbar({ onToggleSidebar, sidebarCollapsed }: NavbarProps) {
  const { user, logout } = useAuth()
  const displayName = user?.email ? user.email.replace(/@.*$/, '') : 'User'

  return (
    <header className="navbar">
      <button
        type="button"
        className="navbar-hamburger"
        onClick={onToggleSidebar}
        aria-label="Toggle sidebar"
      >
        <span className={sidebarCollapsed ? '' : 'open'} />
        <span className={sidebarCollapsed ? '' : 'open'} />
        <span className={sidebarCollapsed ? '' : 'open'} />
      </button>
      <h1 className="navbar-title">Admin Dashboard</h1>
      <div className="navbar-right">
        <div className="navbar-user">
          <div className="navbar-avatar">{displayName.charAt(0).toUpperCase()}</div>
          <span className="navbar-username">{displayName}</span>
        </div>
        <button type="button" className="btn btn-accent navbar-logout" onClick={logout}>
          Logout
        </button>
      </div>
    </header>
  )
}
