import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useProjects } from '../hooks/useProjects'
import { createProject, deleteProject } from '../api'

export default function ProjectsListPage() {
  const navigate = useNavigate()
  const { projects, loading, error, refetch } = useProjects()
  const [isCreating, setIsCreating] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [newProjectName, setNewProjectName] = useState('')

  const handleCreateProject = async (e) => {
    e.preventDefault()
    if (!newProjectName.trim()) return

    setIsCreating(true)
    try {
      const project = await createProject(newProjectName.trim())
      setShowModal(false)
      setNewProjectName('')
      navigate(`/projects/${project.id}`)
    } catch (err) {
      alert(err.message)
    } finally {
      setIsCreating(false)
    }
  }

  const handleDeleteProject = async (projectId, e) => {
    e.stopPropagation()
    if (!confirm('¿Eliminar este proyecto permanentemente?')) return

    try {
      await deleteProject(projectId)
      refetch()
    } catch (err) {
      alert(err.message)
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      draft: { text: 'Borrador', color: 'bg-gray-200 text-gray-800' },
      transcribed: { text: 'Transcrito', color: 'bg-blue-100 text-blue-900' },
      translated: { text: 'Traducido', color: 'bg-purple-100 text-purple-900' },
      dubbed: { text: 'Doblado', color: 'bg-green-100 text-green-900' },
    }
    return badges[status] || badges.draft
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = Math.floor((now - date) / 1000)

    if (diff < 60) return 'Hace un momento'
    if (diff < 3600) return `Hace ${Math.floor(diff / 60)} min`
    if (diff < 86400) return `Hace ${Math.floor(diff / 3600)}h`
    if (diff < 604800) return `Hace ${Math.floor(diff / 86400)}d`

    return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Masthead - Editorial Header */}
      <header className="border-b-4 border-black px-8 py-12">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-end justify-between">
            <div>
              <p className="text-sm uppercase tracking-wider font-mono text-gray-500 mb-2">
                Vol. I — Est. 2026
              </p>
              <h1 className="text-7xl font-black leading-none">
                SUB—DUB
              </h1>
              <p className="text-lg mt-3 text-gray-600 font-light">
                Estudio de Subtitulado y Doblaje
              </p>
            </div>
            <button
              onClick={() => setShowModal(true)}
              className="bg-black text-white px-8 py-4 font-semibold hover:bg-gray-800 transition-colors border-4 border-black hover:translate-x-1 hover:translate-y-1 active:translate-x-0 active:translate-y-0"
              style={{ boxShadow: '4px 4px 0 rgba(0,0,0,1)' }}
            >
              Nuevo Proyecto
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-8 py-16">
        {loading && (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-black border-t-transparent"></div>
            <p className="mt-4 text-gray-500">Cargando proyectos...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-6">
            <p className="text-red-800 font-semibold">Error: {error}</p>
          </div>
        )}

        {!loading && !error && projects.length === 0 && (
          <div className="text-center py-20">
            <h2 className="text-4xl font-bold mb-4">No hay proyectos</h2>
            <p className="text-gray-600 text-lg mb-8">
              Crea tu primer proyecto para comenzar
            </p>
            <button
              onClick={() => setShowModal(true)}
              className="bg-black text-white px-8 py-4 font-semibold hover:bg-gray-800 transition-colors"
            >
              Crear Proyecto
            </button>
          </div>
        )}

        {!loading && projects.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project, index) => {
              const badge = getStatusBadge(project.status)
              return (
                <article
                  key={project.id}
                  onClick={() => navigate(`/projects/${project.id}`)}
                  className="group cursor-pointer bg-white border-2 border-black hover:border-gray-400 transition-all overflow-hidden"
                  style={{
                    boxShadow: '6px 6px 0 rgba(0,0,0,1)',
                    animation: `fadeInUp 0.5s ease-out ${index * 0.1}s backwards`,
                  }}
                >
                  {/* Project Number */}
                  <div className="bg-black text-white px-4 py-2 font-mono text-sm flex justify-between items-center">
                    <span>#{String(index + 1).padStart(3, '0')}</span>
                    <span className="text-xs opacity-60">{formatDate(project.created_at)}</span>
                  </div>

                  {/* Project Content */}
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <h3 className="text-2xl font-bold leading-tight flex-1 group-hover:underline">
                        {project.name}
                      </h3>
                      <button
                        onClick={(e) => handleDeleteProject(project.id, e)}
                        className="ml-4 text-gray-400 hover:text-red-600 transition-colors"
                        title="Eliminar proyecto"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>

                    {/* Status Badge */}
                    <span className={`inline-block px-3 py-1 text-xs font-semibold uppercase tracking-wide ${badge.color}`}>
                      {badge.text}
                    </span>

                    {/* Stats */}
                    <div className="mt-4 pt-4 border-t border-gray-200 text-sm text-gray-600 space-y-1">
                      <p>Creado: {formatDate(project.created_at)}</p>
                      <p>Actualizado: {formatDate(project.updated_at)}</p>
                    </div>
                  </div>

                  {/* Hover Effect */}
                  <div className="h-1 bg-gradient-to-r from-black to-gray-400 transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left"></div>
                </article>
              )
            })}
          </div>
        )}
      </main>

      {/* Create Project Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div
            className="bg-white border-4 border-black max-w-md w-full"
            style={{ boxShadow: '12px 12px 0 rgba(0,0,0,1)' }}
          >
            <div className="bg-black text-white px-6 py-4">
              <h2 className="text-2xl font-bold">Nuevo Proyecto</h2>
            </div>
            <form onSubmit={handleCreateProject} className="p-6">
              <label className="block mb-4">
                <span className="text-sm font-semibold uppercase tracking-wide mb-2 block">
                  Nombre del Proyecto
                </span>
                <input
                  type="text"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  placeholder="Ej: Documental Nature 2024"
                  className="w-full px-4 py-3 border-2 border-black focus:outline-none focus:border-gray-600"
                  autoFocus
                  required
                />
              </label>
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={isCreating}
                  className="flex-1 bg-black text-white px-6 py-3 font-semibold hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isCreating ? 'Creando...' : 'Crear'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false)
                    setNewProjectName('')
                  }}
                  className="px-6 py-3 border-2 border-black hover:bg-gray-100 font-semibold transition-colors"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Keyframes for animations */}
      <style>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  )
}
