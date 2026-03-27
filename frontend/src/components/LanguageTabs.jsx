import { TRANSLATE_LANGUAGES } from '../constants'

const langLabel = (code) => {
  const lang = TRANSLATE_LANGUAGES.find(l => l.code === code)
  return lang ? lang.label : code.toUpperCase()
}

export default function LanguageTabs({ languages, activeLanguage, onSelectLanguage, onAddLanguage, dubLanguages = [] }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      marginTop: '2.5rem',
      marginBottom: '1.5rem',
      flexWrap: 'wrap',
    }}>
      {languages.map((lang) => {
        const isActive = lang === activeLanguage
        const hasDub = dubLanguages.includes(lang)
        return (
          <button
            key={lang}
            onClick={() => onSelectLanguage(lang)}
            style={{
              padding: '0.5rem 1.25rem',
              border: '2px solid black',
              background: isActive ? 'black' : 'white',
              color: isActive ? 'white' : 'black',
              fontWeight: 700,
              fontSize: '0.85rem',
              cursor: 'pointer',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              fontFamily: 'var(--sans)',
              transition: 'all 0.15s',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
          >
            {lang.toUpperCase()}
            {hasDub && (
              <span style={{ fontSize: '0.7rem', opacity: 0.7 }} title="Tiene doblaje">
                ♪
              </span>
            )}
          </button>
        )
      })}
      <button
        onClick={onAddLanguage}
        style={{
          padding: '0.5rem 1rem',
          border: '2px dashed #999',
          background: 'transparent',
          color: '#666',
          fontWeight: 600,
          fontSize: '0.85rem',
          cursor: 'pointer',
          fontFamily: 'var(--sans)',
          transition: 'all 0.15s',
        }}
        onMouseEnter={(e) => { e.target.style.borderColor = 'black'; e.target.style.color = 'black' }}
        onMouseLeave={(e) => { e.target.style.borderColor = '#999'; e.target.style.color = '#666' }}
      >
        + Agregar idioma
      </button>
    </div>
  )
}
