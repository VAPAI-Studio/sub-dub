import { downloadSRT, downloadTXT, downloadJSON, getSpeakerColor } from '../utils'
import SegmentList from './SegmentList'

export default function TranscriptionResult({ result, onUpdateSegment, onSegmentClick }) {
  const allSpeakers = [...new Set(result.segments.map((s) => s.speaker).filter(Boolean))]
  const hasSpeakers = allSpeakers.length > 0

  return (
    <div className="result">
      <div className="result-header">
        <h2>Transcripción</h2>
        <div className="result-actions">
          <span className="language">Idioma: {result.language}</span>
          <div className="download-buttons">
            <button className="download-btn" onClick={() => downloadSRT(result)}>SRT</button>
            <button className="download-btn" onClick={() => downloadTXT(result)}>TXT</button>
            <button className="download-btn" onClick={() => downloadJSON(result)}>JSON</button>
          </div>
        </div>
      </div>

      {hasSpeakers && (
        <div className="speakers-legend">
          {allSpeakers.map((speaker) => (
            <span
              key={speaker}
              className="speaker-badge"
              style={{ backgroundColor: getSpeakerColor(speaker) }}
            >
              {speaker}
            </span>
          ))}
        </div>
      )}

      <SegmentList
        segments={result.segments}
        editable
        allSpeakers={allSpeakers}
        onSegmentClick={onSegmentClick}
        onUpdateSegment={onUpdateSegment}
      />
    </div>
  )
}
