import { LANGUAGES, MODELS } from '../constants'
import '../styles/options.css'

export default function OptionsPanel({ options, onChange }) {
  const update = (key, value) => onChange({ ...options, [key]: value })

  return (
    <div className="options-panel">
      <div className="option">
        <label>Modelo</label>
        <select value={options.modelSize} onChange={(e) => update('modelSize', e.target.value)}>
          {MODELS.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>

      <div className="option">
        <label>Idioma</label>
        <select value={options.language} onChange={(e) => update('language', e.target.value)}>
          {LANGUAGES.map((l) => (
            <option key={l.code} value={l.code}>{l.label}</option>
          ))}
        </select>
      </div>

      <div className="option option-checkbox">
        <label>
          <input
            type="checkbox"
            checked={options.align}
            onChange={(e) => update('align', e.target.checked)}
          />
          Alineamiento por palabra
        </label>
      </div>

      <div className="option option-checkbox">
        <label>
          <input
            type="checkbox"
            checked={options.diarize}
            onChange={(e) => update('diarize', e.target.checked)}
          />
          Diarización (quién habla)
        </label>
      </div>

      {options.diarize && (
        <div className="diarize-options">
          <div className="option">
            <label>Min speakers</label>
            <input
              type="number"
              min="1"
              max="20"
              value={options.minSpeakers}
              onChange={(e) => update('minSpeakers', e.target.value)}
              placeholder="Auto"
            />
          </div>
          <div className="option">
            <label>Max speakers</label>
            <input
              type="number"
              min="1"
              max="20"
              value={options.maxSpeakers}
              onChange={(e) => update('maxSpeakers', e.target.value)}
              placeholder="Auto"
            />
          </div>
        </div>
      )}
    </div>
  )
}
