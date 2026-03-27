import { useState, useEffect, useRef } from 'react'
import { generateDub, getLibraryVoices } from '../api'
import { TRANSLATE_LANGUAGES } from '../constants'
import '../styles/dub.css'

const libraryCache = {}

export default function DubPanel({ translated, voices, projectId = null, result = null, existingDubUrl = null, onDubCreated = null }) {
  const [voiceMap, setVoiceMap] = useState({})
  const [timingMode, setTimingMode] = useState('strict')
  const [dubbing, setDubbing] = useState(false)
  const [dubUrl, setDubUrl] = useState(existingDubUrl)
  const [error, setError] = useState(null)
  const [libraryVoices, setLibraryVoices] = useState([])
  const [loadingLibrary, setLoadingLibrary] = useState(false)

  const targetLang = translated.language

  // Load library voices for the target language
  useEffect(() => {
    if (!targetLang) return

    if (libraryCache[targetLang]) {
      setLibraryVoices(libraryCache[targetLang])
      return
    }

    setLoadingLibrary(true)
    getLibraryVoices(targetLang).then((result) => {
      libraryCache[targetLang] = result
      setLibraryVoices(result)
    }).catch(() => {
      setLibraryVoices([])
    }).finally(() => {
      setLoadingLibrary(false)
    })
  }, [targetLang])

  const allVoices = [...voices, ...libraryVoices]
  const speakers = [...new Set(translated.segments.map((s) => s.speaker).filter(Boolean))]
  const speakerList = speakers.length > 0 ? speakers : ['default']

  const langLabel = TRANSLATE_LANGUAGES.find(l => l.code === targetLang)?.label || targetLang

  const handleVoiceChange = (speaker, voiceId) => {
    setVoiceMap((prev) => ({ ...prev, [speaker]: voiceId }))
  }

  const handleDub = async () => {
    setDubbing(true)
    setError(null)
    if (dubUrl && dubUrl.startsWith('blob:')) URL.revokeObjectURL(dubUrl)
    setDubUrl(null)

    const map = {}
    for (const sp of speakerList) {
      map[sp] = voiceMap[sp] || voices[0]?.voice_id || ''
    }

    try {
      const blob = await generateDub(
        translated.segments, map, voices[0]?.voice_id || '', translated.language, projectId,
        result?.language || null, result?.segments || null, timingMode
      )
      const blobUrl = URL.createObjectURL(blob)
      setDubUrl(blobUrl)
      if (onDubCreated) onDubCreated(translated.language, blobUrl)
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
              <optgroup label="Mis voces">
                {voices.map((v) => (
                  <option key={v.voice_id} value={v.voice_id}>
                    {v.name} ({v.gender}{v.accent ? `, ${v.accent}` : ''})
                  </option>
                ))}
              </optgroup>
              {libraryVoices.length > 0 && (
                <optgroup label={`Librería — ${langLabel}`}>
                  {libraryVoices.map((v) => (
                    <option key={v.voice_id} value={v.voice_id}>
                      {v.name} ({v.gender}{v.accent ? `, ${v.accent}` : ''})
                    </option>
                  ))}
                </optgroup>
              )}
              {loadingLibrary && (
                <optgroup label="Cargando librería...">
                  <option disabled>Cargando voces...</option>
                </optgroup>
              )}
            </select>
          </div>
        ))}
      </div>

      <div className="voice-row" style={{ marginBottom: '1rem' }}>
        <span className="voice-speaker">Modo</span>
        <select
          value={timingMode}
          onChange={(e) => setTimingMode(e.target.value)}
          className="voice-select"
        >
          <option value="strict">Estricto — sincronizado con original</option>
          <option value="natural">Natural — sin acelerar, respeta posición</option>
          <option value="free">Libre — narración corrida</option>
        </select>
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
