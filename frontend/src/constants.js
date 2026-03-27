export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const LANGUAGES = [
  { code: 'auto', label: 'Auto-detectar' },
  { code: 'en', label: 'Inglés' },
  { code: 'es', label: 'Español' },
  { code: 'fr', label: 'Francés' },
  { code: 'de', label: 'Alemán' },
  { code: 'it', label: 'Italiano' },
  { code: 'pt', label: 'Portugués' },
  { code: 'ja', label: 'Japonés' },
  { code: 'zh', label: 'Chino' },
  { code: 'ko', label: 'Coreano' },
  { code: 'ru', label: 'Ruso' },
  { code: 'ar', label: 'Árabe' },
]

export const TRANSLATE_LANGUAGES = [
  { code: 'en', label: 'Inglés' },
  { code: 'es', label: 'Español' },
  { code: 'fr', label: 'Francés' },
  { code: 'de', label: 'Alemán' },
  { code: 'it', label: 'Italiano' },
  { code: 'pt', label: 'Portugués' },
  { code: 'ja', label: 'Japonés' },
  { code: 'zh', label: 'Chino' },
  { code: 'ko', label: 'Coreano' },
  { code: 'ru', label: 'Ruso' },
  { code: 'ar', label: 'Árabe' },
  { code: 'hi', label: 'Hindi' },
  { code: 'tr', label: 'Turco' },
  { code: 'pl', label: 'Polaco' },
  { code: 'nl', label: 'Holandés' },
  { code: 'sv', label: 'Sueco' },
]

export const MODELS = ['tiny', 'base', 'small', 'medium', 'large-v2', 'large-v3']

export const SPEAKER_COLORS = [
  '#2563eb', '#dc2626', '#16a34a', '#9333ea',
  '#ea580c', '#0891b2', '#be185d', '#4f46e5',
]
