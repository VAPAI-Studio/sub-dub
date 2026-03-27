import { useState } from 'react'
import { formatTime, getSpeakerColor } from '../utils'
import '../styles/segments.css'

export default function SegmentList({
  segments,
  editable = false,
  allSpeakers = [],
  onSegmentClick,
  onUpdateSegment,
}) {
  const [expandedSegment, setExpandedSegment] = useState(null)
  const hasWords = segments.some((s) => s.words?.length)

  const handleClick = (seg, i) => {
    onSegmentClick?.(seg.start)
    setExpandedSegment(expandedSegment === i ? null : i)
  }

  return (
    <div className="segments">
      {segments.map((seg, i) => (
        <div
          key={i}
          className={`segment ${expandedSegment === i ? 'expanded' : ''}`}
          onClick={() => handleClick(seg, i)}
        >
          <div className="segment-main">
            {seg.speaker != null && editable ? (
              <select
                className="speaker-select"
                value={seg.speaker}
                style={{ borderColor: getSpeakerColor(seg.speaker), color: getSpeakerColor(seg.speaker) }}
                onClick={(e) => e.stopPropagation()}
                onChange={(e) => onUpdateSegment?.(i, 'speaker', e.target.value)}
              >
                {allSpeakers.map((sp) => (
                  <option key={sp} value={sp}>{sp}</option>
                ))}
              </select>
            ) : seg.speaker ? (
              <span
                className="speaker-badge small"
                style={{ backgroundColor: getSpeakerColor(seg.speaker) }}
              >
                {seg.speaker}
              </span>
            ) : null}

            <span className="timestamp">
              {formatTime(seg.start)} - {formatTime(seg.end)}
            </span>

            {editable ? (
              <input
                className="text-edit"
                value={seg.text}
                onClick={(e) => e.stopPropagation()}
                onChange={(e) => onUpdateSegment?.(i, 'text', e.target.value)}
              />
            ) : (
              <span className="text">{seg.text}</span>
            )}
          </div>

          {hasWords && seg.words && expandedSegment === i && (
            <div className="words">
              {seg.words.map((w, j) => (
                <span key={j} className="word" title={
                  w.start != null ? `${formatTime(w.start)} - ${formatTime(w.end)}` : ''
                }>
                  {w.word}
                </span>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
