import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import UploadPage from './pages/UploadPage'
import ProcessingPage from './pages/ProcessingPage'
import DashboardPage from './pages/DashboardPage'
import MatchesPage from './pages/MatchesPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/upload" replace />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/processing/:matchId" element={<ProcessingPage />} />
          <Route path="/dashboard/:matchId" element={<DashboardPage />} />
          <Route path="/matches" element={<MatchesPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
