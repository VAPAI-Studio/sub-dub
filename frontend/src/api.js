import { API_URL } from './constants'

// ===== Projects API =====
export async function getProjects() {
  const res = await fetch(`${API_URL}/projects`)
  if (!res.ok) throw new Error('Error fetching projects')
  return res.json()
}

export async function createProject(name) {
  const res = await fetch(`${API_URL}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Error creating project')
  }
  return res.json()
}

export async function getProject(projectId) {
  const res = await fetch(`${API_URL}/projects/${projectId}`)
  if (!res.ok) throw new Error('Error fetching project')
  return res.json()
}

export async function deleteProject(projectId) {
  const res = await fetch(`${API_URL}/projects/${projectId}`, {
    method: 'DELETE',
  })
  if (!res.ok) throw new Error('Error deleting project')
  return res.json()
}

// ===== Transcription API =====
export async function transcribe(file, options, projectId = null) {
  const formData = new FormData()
  formData.append('file', file)
  if (projectId) formData.append('project_id', projectId)
  formData.append('model_size', options.modelSize)
  formData.append('language', options.language)
  formData.append('task', options.task)
  formData.append('align', options.align)
  formData.append('diarize', options.diarize)
  if (options.diarize && options.minSpeakers) formData.append('min_speakers', options.minSpeakers)
  if (options.diarize && options.maxSpeakers) formData.append('max_speakers', options.maxSpeakers)

  const res = await fetch(`${API_URL}/transcribe`, { method: 'POST', body: formData })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Error en la transcripción')
  }
  return res.json()
}

export async function translate(segments, sourceLang, targetLang, projectId = null) {
  const res = await fetch(`${API_URL}/translate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      project_id: projectId,
      segments: segments.map((s) => ({
        start: s.start,
        end: s.end,
        text: s.text,
        speaker: s.speaker || null,
      })),
      target_language: targetLang,
      source_language: sourceLang,
    }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Error en la traducción')
  }
  return res.json()
}

export async function getVoices() {
  const res = await fetch(`${API_URL}/voices`)
  if (!res.ok) return []
  const data = await res.json()
  return data.voices || []
}

export async function generateDub(segments, voiceMap, defaultVoiceId, targetLang, projectId = null) {
  const res = await fetch(`${API_URL}/dub`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      project_id: projectId,
      segments: segments.map((s) => ({
        start: s.start,
        end: s.end,
        text: s.text,
        speaker: s.speaker || 'default',
      })),
      voice_map: voiceMap,
      default_voice_id: defaultVoiceId,
      target_language: targetLang,
    }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Error generando doblaje')
  }
  return res.blob()
}
