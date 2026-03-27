import { SPEAKER_COLORS } from './constants'

export function formatTime(seconds) {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  const ms = Math.round((seconds % 1) * 100)
  return `${m}:${String(s).padStart(2, '0')}.${String(ms).padStart(2, '0')}`
}

export function formatSrtTime(seconds) {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  const ms = Math.round((seconds % 1) * 1000)
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')},${String(ms).padStart(3, '0')}`
}

export function getSpeakerColor(speaker) {
  if (!speaker) return '#888'
  const num = parseInt(speaker.replace(/\D/g, ''), 10) || 0
  return SPEAKER_COLORS[num % SPEAKER_COLORS.length]
}

function downloadFile(content, filename, type = 'text/plain') {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export function downloadSRT(result) {
  const lines = result.segments.map((seg, i) => {
    const speaker = seg.speaker ? `[${seg.speaker}] ` : ''
    return `${i + 1}\n${formatSrtTime(seg.start)} --> ${formatSrtTime(seg.end)}\n${speaker}${seg.text.trim()}\n`
  })
  downloadFile(lines.join('\n'), 'transcription.srt')
}

export function downloadTXT(result) {
  const lines = result.segments.map((seg) => {
    const speaker = seg.speaker ? ` [${seg.speaker}]` : ''
    return `[${formatTime(seg.start)} - ${formatTime(seg.end)}]${speaker} ${seg.text.trim()}`
  })
  downloadFile(lines.join('\n'), 'transcription.txt')
}

export function downloadJSON(result) {
  downloadFile(JSON.stringify(result, null, 2), 'transcription.json', 'application/json')
}
