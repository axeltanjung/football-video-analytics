import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { Upload, BarChart3, List, Activity } from 'lucide-react'

const navItems = [
  { to: '/upload', label: 'Upload', icon: Upload },
  { to: '/matches', label: 'Matches', icon: List },
]

export default function Layout() {
  const location = useLocation()

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="w-64 flex-shrink-0 border-r border-white/5 bg-surface-900/50 backdrop-blur-xl flex flex-col">
        <div className="p-6 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-accent/20 flex items-center justify-center">
              <Activity className="w-5 h-5 text-accent-light" />
            </div>
            <div>
              <h1 className="text-sm font-semibold tracking-tight">Football Analytics</h1>
              <p className="text-[11px] text-white/40 font-mono">v1.0.0</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-3 space-y-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? 'active' : ''}`
              }
            >
              <Icon className="w-4 h-4" />
              {label}
            </NavLink>
          ))}

          {location.pathname.startsWith('/dashboard') && (
            <div className="sidebar-link active">
              <BarChart3 className="w-4 h-4" />
              Dashboard
            </div>
          )}
        </nav>

        <div className="p-4 border-t border-white/5">
          <div className="glass p-3 rounded-lg">
            <p className="text-[11px] text-white/40 mb-1">Powered by</p>
            <p className="text-xs font-medium text-white/70">YOLOv8 + DeepSORT</p>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}
