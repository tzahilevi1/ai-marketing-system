import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Campaigns from './pages/Campaigns'
import ContentStudio from './pages/ContentStudio'
import Analytics from './pages/Analytics'
import Agency from './pages/Agency'

function Nav() {
  const { pathname } = useLocation()
  const links = [
    { to: '/', label: 'Dashboard' },
    { to: '/campaigns', label: 'Campaigns' },
    { to: '/content-studio', label: 'Content Studio' },
    { to: '/analytics', label: 'Analytics' },
    { to: '/agency', label: 'Agency' },
  ]
  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <span className="text-xl font-bold text-primary-600">AI Marketing</span>
        <div className="flex gap-6">
          {links.map(l => (
            <Link
              key={l.to}
              to={l.to}
              className={`text-sm font-medium ${pathname === l.to ? 'text-primary-600' : 'text-gray-600 hover:text-gray-900'}`}
            >
              {l.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  )
}

function AppShell() {
  const { pathname } = useLocation()
  const isAgency = pathname === '/agency'

  if (isAgency) {
    return (
      <Routes>
        <Route path="/agency" element={<Agency />} />
      </Routes>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Nav />
      <main className="max-w-7xl mx-auto px-6 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/campaigns" element={<Campaigns />} />
          <Route path="/content-studio" element={<ContentStudio />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  )
}
