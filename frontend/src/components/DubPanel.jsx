import { useState } from 'react'
import { generateDub } from '../api'
import '../styles/dub.css'

export default function DubPanel({ translated, voices, projectId = null }) {
  const [voiceMap, setVoiceMap] = useState({})
  const [dubbing, setDubbing] = useState(false)
  const [dubUrl, setDubUrl] = useState(null)
  const [error, setError] = useState(null)

  const speakers = [...new Set(translated.segments.map((s) => s.speaker).filter(Boolean))]
  const speakerList = speakers.length > 0 ? speakers : ['default']

  const handleVoiceChange = (speaker, voiceId) => {
    setVoiceMap((prev) => ({ ...prev, [speaker]: voiceId }))
  }

  const handleDub = async () => {
    setDubbing(true)
    setError(null)
    if (dubUrl) URL.revokeObjectURL(dubUrl)
    setDubUrl(null)

    const map = {}
    for (const sp of speakerList) {
      map[sp] = voiceMap[sp] || voices[0]?.voice_id || ''
    }

    try {
      const blob = await generateDub(
        translated.segments, map, voices[0]?.voice_id || '', translated.language, projectId
      )
      setDubUrl(URL.createObjectURL(blob))
    } catch (err) {
      setError(err.message)
    } finally {
      setDubbing(false)
    }
  }

  return (
    <div className="dub-section">
      <h2>Doblaje</h2>

      <div className="voice-mapping">
        {speakerList.map((speaker) => (
          <div key={speaker} className="voice-row">
            <span className="voice-speaker">
              {speaker === 'default' ? 'Voz' : speaker}
            </span>
            <select
              value={voiceMap[speaker] || voices[0]?.voice_id || ''}
              onChange={(e) => handleVoiceChange(speaker, e.target.value)}
              className="voice-select"
            >
              {voices.map((v) => (
                <option key={v.voice_id} value={v.voice_id}>
                  {v.name} ({v.gender}{v.accent ? `, ${v.accent}` : ''})
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>

      <button onClick={handleDub} disabled={dubbing} className="dub-btn">
        {dubbing ? 'Generando doblaje...' : 'Generar doblaje'}
      </button>

      {dubbing && (
        <div className="loading">
          <div className="spinner" />
          <p>Generando audio con ElevenLabs... esto puede tardar.</p>
        </div>
      )}

      {error && <p className="error">{error}</p>}

      {dubUrl && (
        <div className="dub-result">
          <h3>Audio doblado</h3>
          <audio controls src={dubUrl} className="audio-player" />
          <a href={dubUrl} download="dub.mp3" className="download-btn dub-download">
            Descargar MP3
          </a>
        </div>
      )}
    </div>
  )
}
