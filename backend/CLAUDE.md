# Backend — FastAPI

## Stack

- **Framework**: FastAPI + Uvicorn
- **Language**: Python 3
- **Validation**: Pydantic models (`models.py`)
- **Config**: `config.py` + `.env` (python-dotenv)
- **Database**: Supabase (PostgreSQL) for project persistence

## Structure

```
backend/
├── main.py              # App init, CORS, router registration
├── config.py            # Device detection (CUDA/CPU), allowed formats, models list
├── models.py            # Pydantic request/response schemas
├── requirements.txt
├── .env                 # API keys (HF_TOKEN, ANTHROPIC_API_KEY, ELEVENLABS_API_KEY, SUPABASE_URL, SUPABASE_KEY)
├── routes/
│   ├── transcribe.py    # POST /transcribe — audio upload + WhisperX ASR
│   ├── translate.py     # POST /translate — Claude-powered translation
│   ├── dub.py           # POST /dub, GET /voices — ElevenLabs TTS
│   └── projects.py      # CRUD endpoints for projects
├── services/
│   ├── asr.py           # WhisperX transcription, alignment, diarization
│   ├── translation.py   # Anthropic Claude translation logic
│   ├── tts.py           # ElevenLabs TTS generation + audio timeline assembly
│   └── supabase_client.py  # Supabase client singleton
└── uploads/             # Temporary audio file storage
```

## Services Detail

### `services/asr.py` — Transcription
- Loads WhisperX model by size (tiny → large-v3).
- Transcribes audio into timed segments.
- Optional word-level alignment via WhisperX alignment model.
- Optional speaker diarization via Hugging Face pyannote pipeline (`HF_TOKEN` required).

### `services/translation.py` — Translation
- Uses Anthropic Claude (`claude-sonnet-4-20250514`).
- Sends segments with `[index]` prefixes to preserve mapping.
- Prompt instructs Claude to maintain segment count and indices.

### `services/tts.py` — Dubbing
- Calls ElevenLabs API (`eleven_multilingual_v2` model) per segment.
- Creates a silent base track matching the total audio duration.
- If generated audio is longer than the segment slot, speeds it up (max 1.8x) or truncates.
- Overlays each segment's audio at the correct timeline position.
- Exports final composite MP3 (192kbps, 44.1kHz).
- Uses `pydub` for all audio manipulation.

### `services/supabase_client.py` — Database
- Singleton Supabase client for PostgreSQL database operations.
- Requires `SUPABASE_URL` and `SUPABASE_KEY` environment variables.
- Used by project routes to persist workflow state.

## Running

```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Config Notes

- `config.py` auto-detects CUDA and sets `float16`; falls back to CPU with `int8`.
- CORS allows only `http://localhost:5173`.
- Allowed models: `tiny`, `base`, `small`, `medium`, `large-v2`, `large-v3`.
- Allowed audio extensions: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.webm`, `.mp4`, `.wma`.

## API Routes

### Projects (`routes/projects.py`)
- **GET /projects/** — List all projects (ordered by creation date)
- **POST /projects/** — Create new project (requires `name`)
- **GET /projects/{project_id}** — Get project with all related data (audio, transcription, translation, dub)
- **PUT /projects/{project_id}** — Update project (name, status)
- **DELETE /projects/{project_id}** — Delete project (cascades to related data)

## Key Patterns

- Routes are thin — they validate input and delegate to services.
- Projects are persisted in Supabase with related audio, transcription, translation, and dub data.
- File uploads are saved to `uploads/`, processed, then can be cleaned up.
- Translation preserves segment indices via `[N]` prefix convention in the Claude prompt.
- TTS voice mapping is per-speaker: the frontend sends a `voice_map` dict (`speaker_id → voice_id`).
