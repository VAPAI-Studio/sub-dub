import { useRef } from 'react'
import '../styles/upload.css'

export default function UploadPanel({ file, audioUrl, audioRef, onFileChange }) {
  const fileInputRef = useRef(null)

  return (
    <div className="upload-panel">
      <div className="upload-section">
        <input
          ref={fileInputRef}
          type="file"
          accept=".mp3,.wav,.m4a,.flac,.ogg,.webm,.mp4,.wma"
          onChange={onFileChange}
          id="file-input"
        />
        <label htmlFor="file-input" className="file-label">
          {file ? file.name : 'Seleccionar archivo de audio'}
        </label>
      </div>

      {audioUrl && (
        <audio ref={audioRef} controls src={audioUrl} className="audio-player" />
      )}
    </div>
  )
}
