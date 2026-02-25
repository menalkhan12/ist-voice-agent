import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Navbar } from './Navbar'
import { Sidebar } from './Sidebar'
import './DashboardLayout.css'

export function DashboardLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)

  const toggleSidebar = () => {
    setSidebarCollapsed(prev => !prev)
    setMobileSidebarOpen(prev => !prev)
  }

  return (
    <div className="app">
      <Navbar
        onToggleSidebar={toggleSidebar}
        sidebarCollapsed={sidebarCollapsed}
      />
      <Sidebar collapsed={sidebarCollapsed} mobileOpen={mobileSidebarOpen} />
      <main
        className={`main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''} ${mobileSidebarOpen ? 'sidebar-expanded-mobile' : ''}`}
      >
        <Outlet />
      </main>
    </div>
  )
}
