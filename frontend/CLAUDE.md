# Frontend — React SPA

## Stack

- **Framework**: React 19 (JSX, hooks)
- **Build Tool**: Vite 8
- **Styling**: Plain CSS (scoped per component + global variables)
- **HTTP**: Native `fetch` (no axios)
- **State**: React hooks only (`useState`, `useRef`, `useEffect`) — no external state library

## Structure

```
frontend/
├── src/
│   ├── main.jsx                 # React DOM entry point
│   ├── App.jsx                  # Main orchestrator — holds all global state
│   ├── App.css                  # App-level styles
│   ├── index.css                # Global styles, CSS variables, dark mode
│   ├── api.js                   # All backend API calls (4 functions)
│   ├── constants.js             # API_URL, languages, models, speaker colors
│   ├── utils.js                 # Helper functions (SRT/TXT/JSON export)
│   ├── components/
│   │   ├── UploadPanel.jsx      # File input + audio player
│   │   ├── OptionsPanel.jsx     # Transcription config (model, language, diarize, align)
│   │   ├── TranscriptionResult.jsx  # Segment display + download buttons
│   │   ├── SegmentList.jsx      # Clickable/editable segments with speaker badges
│   │   ├── TranslatePanel.jsx   # Language selector + trigger translation
│   │   └── DubPanel.jsx         # Speaker-to-voice mapping + generate dubbed audio
│   └── styles/
│       ├── upload.css
│       ├── options.css
│       ├── segments.css
│       ├── translate.css
│       └── dub.css
├── index.html
├── package.json
├── vite.config.js
└── eslint.config.js
```

## App Flow

1. **UploadPanel** — User selects an audio file; an HTML5 `<audio>` player appears.
2. **OptionsPanel** — User picks model size, language, task, alignment, diarization.
3. **Transcribe** button → `api.transcribe()` → results populate `TranscriptionResult`.
4. **TranscriptionResult / SegmentList** — Shows timed segments with speaker badges (color-coded). Text and speaker fields are editable. Downloads available in SRT, TXT, JSON.
5. **TranslatePanel** — User picks target language → `api.translate()` → translated segments shown separately with their own download buttons.
6. **DubPanel** — Appears when translation + voices are available. User maps each speaker to an ElevenLabs voice → `api.generateDub()` → returns MP3 with audio player + download.

## API Layer (`api.js`)

| Function          | Endpoint      | Notes                                    |
|-------------------|--------------|------------------------------------------|
| `transcribe()`    | POST /transcribe | Sends FormData (file + options)       |
| `translate()`     | POST /translate  | Sends JSON (segments + languages)     |
| `getVoices()`     | GET /voices      | Fetches ElevenLabs voice catalog      |
| `generateDub()`   | POST /dub        | Sends JSON, receives MP3 blob         |

**Base URL**: `http://localhost:8000` (defined in `constants.js`).

## State Management

All state lives in `App.jsx` and is passed as props:
- `file`, `audioUrl` — selected audio
- `result` — transcription response (segments)
- `translated` — translation response
- `voices` — ElevenLabs voice list (fetched on mount)
- `options` — transcription settings object
- `loading`, `error` — UI state
- `audioRef` — ref to `<audio>` element for segment click-to-play

## Styling

- Color scheme: blue (#2563eb) primary, purple (#7c3aed) translation, green (#059669) dubbing.
- CSS variables in `:root` for theming.
- Dark mode via `prefers-color-scheme`.
- 8-color palette for speaker badges (defined in `constants.js`).

## Scripts

```bash
npm run dev      # Vite dev server (HMR) — http://localhost:5173
npm run build    # Production build → dist/
npm run lint     # ESLint
npm run preview  # Preview production build
```

## Key Patterns

- Components are presentational; `App.jsx` is the single source of truth for state.
- Segment text is editable in-place — changes update the local state before export/translation.
- `SegmentList` segments are clickable: sets `audioRef.currentTime` to segment start time.
- Export utils (`utils.js`) generate SRT, TXT, JSON from the segments array.
- No routing library — it's a single-page workflow, not a multi-page app.
