# SUB-DUB - Subtitles & Dubbing Tool

## Project Overview

SUB-DUB is a web application for generating subtitles and dubbing from audio/video files. The workflow is: **upload audio → transcribe → translate → dub with synthetic voices**.

- **Frontend**: React 19 SPA (Vite) — `frontend/`
- **Backend**: FastAPI (Python) — `backend/`
- **UI Language**: Spanish

## Architecture

```
whisperX-dev/
├── frontend/          # React SPA (Vite, plain CSS)
├── backend/           # FastAPI REST API
└── audios/            # Sample audio files
```

### Core Pipeline

1. **Transcription (ASR)**: WhisperX models transcribe audio to timed text segments, with optional word-level alignment and speaker diarization.
2. **Translation**: Claude API (`claude-sonnet-4-20250514`) translates subtitle segments preserving timing and structure.
3. **Dubbing (TTS)**: ElevenLabs API generates voiced audio per segment with speaker-to-voice mapping, speed adjustment, and timeline overlay.

### External Services

| Service       | Purpose                  | Env Variable         |
|---------------|--------------------------|----------------------|
| WhisperX      | Speech recognition (local) | —                  |
| Anthropic     | Subtitle translation     | `ANTHROPIC_API_KEY`  |
| ElevenLabs    | Text-to-Speech dubbing   | `ELEVENLABS_API_KEY` |
| Hugging Face  | Speaker diarization      | `HF_TOKEN`           |

## Running the Project

### Backend

```bash
cd backend
pip install -r requirements.txt
# Create .env with HF_TOKEN, ANTHROPIC_API_KEY, ELEVENLABS_API_KEY
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev    # Starts on http://localhost:5173
```

CORS is configured for `localhost:5173` → `localhost:8000`.

## API Endpoints

| Method | Endpoint     | Description                              |
|--------|-------------|------------------------------------------|
| POST   | /transcribe | Upload audio, returns timed segments     |
| POST   | /translate  | Translate segments to target language     |
| GET    | /voices     | List available ElevenLabs voices         |
| POST   | /dub        | Generate dubbed MP3 from segments + voices |

## Key Conventions

- No database — the app is stateless, processes files in-memory.
- Audio uploads are stored temporarily in `backend/uploads/`.
- Supported audio formats: mp3, wav, m4a, flac, ogg, webm, mp4, wma.
- 16 supported languages for transcription/translation (en, es, fr, de, it, pt, ja, zh, ko, ru, ar, hi, tr, pl, nl, sv).
- GPU (CUDA) is used if available; falls back to CPU with int8 quantization.
