import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import ProjectsListPage from './pages/ProjectsListPage'
import WorkspacePage from './pages/WorkspacePage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ProjectsListPage />} />
        <Route path="/projects/:projectId" element={<WorkspacePage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
