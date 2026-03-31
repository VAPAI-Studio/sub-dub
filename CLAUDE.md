# SUB-DUB - Subtitles & Dubbing Tool

## Project Overview

SUB-DUB is a web application for generating subtitles and dubbing from audio/video files. The workflow is: **upload audio → transcribe → translate (multi-language) → dub with synthetic voices**.

- **Frontend**: React 19 SPA (Vite + Tailwind v4) — `frontend/` — deployed on Vercel
- **Backend**: FastAPI (Python) — `backend/` — runs locally, exposed via Cloudflare Tunnel
- **Database**: Supabase (PostgreSQL) — Cloud or local
- **Storage**: Supabase Storage (buckets: `audio-inputs`, `audio-dubs`)
- **UI Language**: Spanish

## Architecture

```
sub-dub/
├── frontend/          # React SPA (Vite, Tailwind v4)
├── backend/           # FastAPI REST API
├── supabase/          # Config + SQL migrations
└── audios/            # Sample audio files
```

### Deployment Architecture

```
[Vercel: frontend] → [Cloudflare Tunnel] → [Local PC: backend + GPU]
       ↓                                           ↓
[Supabase Cloud: DB + Storage] ←──────────────────┘
```

### Core Pipeline

1. **Transcription (ASR)**: WhisperX models transcribe audio to timed text segments, with optional word-level alignment and speaker diarization.
2. **Translation**: Claude API (`claude-sonnet-4-20250514`) translates subtitle segments preserving timing and structure. Supports multiple target languages per project.
3. **Dubbing (TTS)**: ElevenLabs API generates voiced audio per segment with speaker-to-voice mapping. Three timing modes: strict (synced), natural (no speedup), free (sequential narration). Phoneme-based speed estimation via `phonemizer` + `espeak-ng`.

### External Services

| Service       | Purpose                    | Env Variable         |
|---------------|----------------------------|----------------------|
| WhisperX      | Speech recognition (local) | —                    |
| Anthropic     | Subtitle translation       | `ANTHROPIC_API_KEY`  |
| ElevenLabs    | Text-to-Speech dubbing     | `ELEVENLABS_API_KEY` |
| Hugging Face  | Speaker diarization        | `HF_TOKEN`           |
| Supabase      | Database + File Storage    | `SUPABASE_URL`, `SUPABASE_KEY` |

## Running the Project

### Backend

```bash
cd backend
pip install -r requirements.txt
# Create .env with HF_TOKEN, ANTHROPIC_API_KEY, ELEVENLABS_API_KEY, SUPABASE_URL, SUPABASE_KEY
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

### Frontend

```bash
cd frontend
npm install
npm run dev    # Starts on http://localhost:5173
```

CORS is configured for `localhost:5173`, `subdub-api.vapai.studio`, and `sub-dub-psi.vercel.app`.

## API Endpoints

| Method | Endpoint                          | Description                              |
|--------|-----------------------------------|------------------------------------------|
| GET    | /projects/                        | List all projects                        |
| POST   | /projects/                        | Create new project                       |
| GET    | /projects/{id}                    | Get project with all related data        |
| PUT    | /projects/{id}                    | Update project                           |
| DELETE | /projects/{id}                    | Delete project (cascade)                 |
| POST   | /projects/{id}/upload-audio       | Upload audio file to Supabase Storage    |
| GET    | /projects/{id}/audio              | Serve audio (redirects to Storage URL)   |
| GET    | /projects/{id}/dub-audio?lang=xx  | Serve dub audio by language              |
| POST   | /transcribe                       | Upload audio, returns timed segments     |
| POST   | /translate                        | Translate segments (upsert by language)  |
| GET    | /voices                           | List user's ElevenLabs voices            |
| GET    | /voices/library?lang=xx           | Browse public ElevenLabs voice library   |
| POST   | /dub                              | Generate dubbed MP3 from segments + voices |

## Key Conventions

- **Multi-language**: Each project can have multiple translations and dubs (one per target language). UI uses tabs to switch between languages.
- **File Storage**: Audio inputs and dubs are stored in Supabase Storage buckets. WhisperX uses temp files downloaded from Storage during transcription.
- **Timing modes**: Dub supports three modes — `strict` (synced to original), `natural` (no speedup), `free` (sequential narration).
- **Phoneme estimation**: `duration_estimator.py` uses `phonemizer` + language speaking rates to pre-calculate ElevenLabs speed parameter.
- **Translation upsert**: Translating to an existing language replaces it (with frontend confirmation).
- Supported audio formats: mp3, wav, m4a, flac, ogg, webm, mp4, wma.
- 16 supported languages for transcription/translation.
- GPU (CUDA) is used if available; falls back to CPU with int8 quantization.
- Backend port: 8002. Exposed via Cloudflare Tunnel at `subdub-api.vapai.studio`.
