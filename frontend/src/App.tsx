import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Feed from './pages/Feed'
import Trends from './pages/Trends'
import People from './pages/People'
import Settings from './pages/Settings'

const navItems = [
  { to: '/', label: 'Feed' },
  { to: '/trends', label: 'Trends' },
  { to: '/people', label: 'People' },
  { to: '/settings', label: 'Settings' },
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-950 text-gray-100">
        <nav className="border-b border-gray-800 px-6 py-3 flex items-center gap-6">
          <span className="text-lg font-semibold text-white">Info Tracker</span>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `text-sm ${isActive ? 'text-white font-medium' : 'text-gray-400 hover:text-gray-200'}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <main className="max-w-6xl mx-auto px-6 py-6">
          <Routes>
            <Route path="/" element={<Feed />} />
            <Route path="/trends" element={<Trends />} />
            <Route path="/people" element={<People />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
