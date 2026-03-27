import { useState } from 'react'
import { TRANSLATE_LANGUAGES } from '../constants'
import { downloadSRT, downloadTXT, downloadJSON } from '../utils'
import { translate as apiTranslate } from '../api'
import SegmentList from './SegmentList'
import '../styles/translate.css'

export default function TranslatePanel({
  result,
  activeTranslation,
  onTranslated,
  onSegmentClick,
  projectId = null,
  existingLanguages = [],
  showAddForm = false,
}) {
  const [targetLang, setTargetLang] = useState('en')
  const [translating, setTranslating] = useState(false)
  const [error, setError] = useState(null)
  const [showConfirm, setShowConfirm] = useState(false)

  const handleTranslate = async () => {
    // Check if language already exists
    if (existingLanguages.includes(targetLang)) {
      setShowConfirm(true)
      return
    }
    doTranslate()
  }

  const doTranslate = async () => {
    setShowConfirm(false)
    setTranslating(true)
    setError(null)
    try {
      const data = await apiTranslate(result.segments, result.language, targetLang, projectId)
      onTranslated(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setTranslating(false)
    }
  }

  const langLabel = (code) => {
    const lang = TRANSLATE_LANGUAGES.find(l => l.code === code)
    return lang ? lang.label : code.toUpperCase()
  }

  return (
    <div className="translate-section">
      {showAddForm && (
        <>
          <h2>Traducción</h2>
          <div className="translate-controls">
            <select value={targetLang} onChange={(e) => setTargetLang(e.target.value)}>
              {TRANSLATE_LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>{l.label}</option>
              ))}
            </select>
            <button onClick={handleTranslate} disabled={translating} className="translate-btn">
              {translating ? 'Traduciendo...' : 'Traducir'}
            </button>
          </div>

          {showConfirm && (
            <div style={{
              padding: '1rem',
              border: '2px solid black',
              background: '#fef3c7',
              marginBottom: '1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '1rem',
            }}>
              <p style={{ margin: 0, fontWeight: 600 }}>
                Ya existe una traducción en {langLabel(targetLang)}. ¿Reemplazar?
              </p>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  onClick={doTranslate}
                  style={{
                    padding: '0.5rem 1rem', background: 'black', color: 'white',
                    border: 'none', fontWeight: 600, cursor: 'pointer',
                  }}
                >
                  Sí, reemplazar
                </button>
                <button
                  onClick={() => setShowConfirm(false)}
                  style={{
                    padding: '0.5rem 1rem', background: 'white', color: 'black',
                    border: '2px solid black', fontWeight: 600, cursor: 'pointer',
                  }}
                >
                  Cancelar
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {translating && (
        <div className="loading">
          <div className="spinner" />
          <p>Traduciendo con Claude...</p>
        </div>
      )}

      {error && <p className="error">{error}</p>}

      {activeTranslation && !translating && (
        <div className="result">
          <div className="result-header">
            <h3>Traducción — {langLabel(activeTranslation.language)}</h3>
            <div className="result-actions">
              <div className="download-buttons">
                <button className="download-btn" onClick={() => downloadSRT(activeTranslation)}>SRT</button>
                <button className="download-btn" onClick={() => downloadTXT(activeTranslation)}>TXT</button>
                <button className="download-btn" onClick={() => downloadJSON(activeTranslation)}>JSON</button>
              </div>
            </div>
          </div>
          <SegmentList segments={activeTranslation.segments} onSegmentClick={onSegmentClick} />
        </div>
      )}
    </div>
  )
}
