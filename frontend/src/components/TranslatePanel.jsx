import { useState } from 'react'
import { TRANSLATE_LANGUAGES } from '../constants'
import { downloadSRT, downloadTXT, downloadJSON, getSpeakerColor } from '../utils'
import { translate as apiTranslate } from '../api'
import SegmentList from './SegmentList'
import '../styles/translate.css'

export default function TranslatePanel({ result, translated, onTranslated, onSegmentClick, projectId = null }) {
  const [targetLang, setTargetLang] = useState('en')
  const [translating, setTranslating] = useState(false)
  const [error, setError] = useState(null)

  const handleTranslate = async () => {
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

  return (
    <div className="translate-section">
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

      {translating && (
        <div className="loading">
          <div className="spinner" />
          <p>Traduciendo con Claude...</p>
        </div>
      )}

      {error && <p className="error">{error}</p>}

      {translated && (
        <div className="result">
          <div className="result-header">
            <h3>Resultado traducido</h3>
            <div className="result-actions">
              <span className="language">
                {TRANSLATE_LANGUAGES.find((l) => l.code === translated.language)?.label || translated.language}
              </span>
              <div className="download-buttons">
                <button className="download-btn" onClick={() => downloadSRT(translated)}>SRT</button>
                <button className="download-btn" onClick={() => downloadTXT(translated)}>TXT</button>
                <button className="download-btn" onClick={() => downloadJSON(translated)}>JSON</button>
              </div>
            </div>
          </div>
          <SegmentList segments={translated.segments} onSegmentClick={onSegmentClick} />
        </div>
      )}
    </div>
  )
}
