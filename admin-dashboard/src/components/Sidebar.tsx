import { NavLink } from 'react-router-dom'
import './Sidebar.css'

const navItems = [
  { to: '/profile', label: 'User Profile', icon: '👤' },
  { to: '/call-logs', label: 'Call Logs', icon: '📋' },
  { to: '/reports', label: 'Reports & Analytics', icon: '📊' },
  { to: '/database', label: 'Database (Knowledge Base)', icon: '📁' },
  { to: '/settings', label: 'Settings', icon: '⚙️' },
]

interface SidebarProps {
  collapsed: boolean
  mobileOpen?: boolean
}

export function Sidebar({ collapsed, mobileOpen }: SidebarProps) {
  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}>
      <nav className="sidebar-nav">
        {navItems.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            title={collapsed ? label : undefined}
          >
            <span className="sidebar-icon">{icon}</span>
            {!collapsed && <span className="sidebar-label">{label}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
