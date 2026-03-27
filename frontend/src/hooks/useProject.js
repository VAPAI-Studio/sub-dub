import { useState, useEffect } from 'react'
import { getProject } from '../api'

export function useProject(projectId) {
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!projectId) {
      setLoading(false)
      return
    }

    loadProject()
  }, [projectId])

  async function loadProject() {
    try {
      setLoading(true)
      const data = await getProject(projectId)
      setProject(data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return { project, loading, error, refetch: loadProject }
}
