# SUB-DUB - Subtitles & Dubbing Tool

Herramienta web para generar subtítulos y doblaje desde archivos de audio/video. El flujo de trabajo es: **subir audio → transcribir → traducir (multi-idioma) → doblar con voces sintéticas**.

## Características

- **Transcripción (ASR)**: WhisperX para transcribir audio a texto con marcas de tiempo
- **Traducción multi-idioma**: Claude AI para traducir subtítulos a múltiples idiomas simultáneamente
- **Doblaje (TTS)**: ElevenLabs para generar voces sintéticas con mapeo de hablantes y 3 modos de timing
- **Librería de voces**: Acceso a voces propias + librería pública de ElevenLabs filtradas por idioma
- **Estimación por fonemas**: Cálculo inteligente de velocidad de habla usando `phonemizer` para mejor calidad
- **Persistencia**: Supabase (PostgreSQL + Storage) para guardar proyectos, archivos y datos

## Requisitos Previos

- **Python 3.10+** (para backend)
- **Node.js 18+** y npm (para frontend)
- **FFmpeg** instalado y en PATH (requerido por pydub)
- **espeak-ng** instalado (requerido por phonemizer para estimación de fonemas)
- **Docker Desktop** (para Supabase local)
- **Supabase CLI** (para desarrollo local)
- GPU NVIDIA con CUDA (opcional, mejora rendimiento de transcripción)

## API Keys Necesarias

1. **Hugging Face Token**: https://huggingface.co/settings/tokens (para diarización de hablantes)
2. **Anthropic API Key**: https://console.anthropic.com/ (para traducción con Claude)
3. **ElevenLabs API Key**: https://elevenlabs.io/app/settings/api-keys (para TTS)
4. **Supabase URL + Key**: https://supabase.com/dashboard/project/_/settings/api (o local con CLI)

## Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/sub-dub.git
cd sub-dub
```

### 2. Configurar Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tus API keys
```

**Configurar `.env` del backend:**

```env
HF_TOKEN=tu_token_de_huggingface
ANTHROPIC_API_KEY=tu_api_key_de_anthropic
ELEVENLABS_API_KEY=tu_api_key_de_elevenlabs

# --- Local ---
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_KEY=tu_supabase_key
# --- Cloud ---
# SUPABASE_URL=https://tu-proyecto.supabase.co
# SUPABASE_KEY=tu_supabase_anon_key
```

### 3. Configurar Frontend

```bash
cd ../frontend
npm install
cp .env.example .env
```

**Configurar `.env` del frontend:**

```env
VITE_API_URL=http://localhost:8002

# --- Local ---
VITE_SUPABASE_URL=http://127.0.0.1:54321
VITE_SUPABASE_ANON_KEY=tu_supabase_anon_key
# --- Cloud ---
# VITE_SUPABASE_URL=https://tu-proyecto.supabase.co
# VITE_SUPABASE_ANON_KEY=tu_supabase_anon_key
```

### 4. Configurar Base de Datos (Supabase)

**Opción A: Supabase Local (Recomendado para desarrollo)**

```bash
# Instalar Supabase CLI (Windows con scoop)
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase

# Iniciar Supabase local (desde la raíz del proyecto)
supabase start

# Copiar las credenciales que aparecen en la consola a tus archivos .env

# Aplicar migraciones
supabase db reset
```

**Opción B: Supabase Cloud**

1. Crear proyecto en https://supabase.com/dashboard
2. Ir a Settings → API y copiar URL + anon key
3. Linkear: `supabase link --project-ref TU_PROJECT_ID`
4. Aplicar migraciones: `supabase db push`

### 5. Instalar espeak-ng (para estimación de fonemas)

**Windows:**
```bash
choco install espeak-ng
# O descargar desde: https://github.com/espeak-ng/espeak-ng/releases
```

**Mac:**
```bash
brew install espeak-ng
```

**Linux:**
```bash
sudo apt install espeak-ng
```

### 6. Instalar FFmpeg

**Windows:**
```bash
choco install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

## Ejecutar el Proyecto

### Backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

El backend estará disponible en: http://localhost:8002

### Frontend

```bash
cd frontend
npm run dev
```

El frontend estará disponible en: http://localhost:5173

## Deploy (Producción)

### Arquitectura

```
[Vercel: frontend] → [Cloudflare Tunnel] → [PC local: backend + GPU]
       ↓                                           ↓
[Supabase Cloud: DB + Storage] ←──────────────────┘
```

- **Frontend**: Vercel (deploy automático desde GitHub, root: `frontend`)
- **Backend**: PC local con GPU, expuesto via Cloudflare Tunnel
- **Base de datos + Storage**: Supabase Cloud

### URLs de producción

- Frontend: `https://sub-dub-psi.vercel.app`
- Backend API: `https://subdub-api.vapai.studio`

## Estructura del Proyecto

```
sub-dub/
├── backend/
│   ├── routes/
│   │   ├── transcribe.py    # POST /transcribe
│   │   ├── translate.py     # POST /translate (upsert por idioma)
│   │   ├── dub.py           # POST /dub, GET /voices, GET /voices/library
│   │   └── projects.py      # CRUD + upload/serve audio via Storage
│   ├── services/
│   │   ├── asr.py           # WhisperX transcription
│   │   ├── translation.py   # Claude translation
│   │   ├── tts.py           # ElevenLabs TTS (3 timing modes)
│   │   ├── duration_estimator.py  # Phoneme-based speed estimation
│   │   └── supabase_client.py     # DB + Storage helpers
│   ├── models.py
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadPanel.jsx
│   │   │   ├── OptionsPanel.jsx
│   │   │   ├── TranscriptionResult.jsx
│   │   │   ├── SegmentList.jsx
│   │   │   ├── TranslatePanel.jsx
│   │   │   ├── DubPanel.jsx
│   │   │   └── LanguageTabs.jsx
│   │   ├── pages/
│   │   │   ├── ProjectsListPage.jsx
│   │   │   └── WorkspacePage.jsx
│   │   ├── hooks/
│   │   ├── api.js
│   │   ├── constants.js
│   │   └── utils.js
│   └── package.json
├── supabase/
│   ├── config.toml
│   └── migrations/
│       ├── 20260326000001_create_projects_schema.sql
│       ├── 20260327000001_add_multi_language_support.sql
│       └── 20260327000002_create_storage_buckets.sql
└── audios/
```

## API Endpoints

| Método | Endpoint                          | Descripción                                    |
|--------|-----------------------------------|------------------------------------------------|
| GET    | `/projects/`                      | Listar todos los proyectos                     |
| POST   | `/projects/`                      | Crear nuevo proyecto                           |
| GET    | `/projects/{id}`                  | Obtener proyecto con datos relacionados        |
| PUT    | `/projects/{id}`                  | Actualizar proyecto                            |
| DELETE | `/projects/{id}`                  | Eliminar proyecto (cascada)                    |
| POST   | `/projects/{id}/upload-audio`     | Subir audio a Supabase Storage                 |
| GET    | `/projects/{id}/audio`            | Servir audio (redirect a Storage URL)          |
| GET    | `/projects/{id}/dub-audio?lang=xx`| Servir audio de dub por idioma                 |
| POST   | `/transcribe`                     | Subir audio y transcribir con WhisperX         |
| POST   | `/translate`                      | Traducir segmentos (upsert por idioma)         |
| GET    | `/voices`                         | Listar voces propias de ElevenLabs             |
| GET    | `/voices/library?lang=xx`         | Buscar voces en librería pública por idioma    |
| POST   | `/dub`                            | Generar audio doblado (3 modos de timing)      |

## Flujo de Uso

1. **Crear proyecto** → asignar nombre
2. **Subir audio** → se guarda en Supabase Storage
3. **Transcribir** → WhisperX genera segmentos con timestamps
4. **Traducir** → Claude traduce a uno o más idiomas (tabs)
5. **Doblar** → ElevenLabs genera audio por idioma con voces asignadas
6. **Descargar** → Subtítulos (SRT/TXT/JSON) + audio MP3

## Modos de Doblaje

| Modo | Descripción | Ideal para |
|------|-------------|------------|
| **Estricto** | Sincronizado con timestamps originales (acelera/recorta si es necesario) | Video con lip-sync |
| **Natural** | Respeta posición de inicio pero no acelera ni recorta | Calidad de voz prioritaria |
| **Libre** | Concatenación secuencial sin timeline | Audiolibros, podcasts |

## Idiomas Soportados

16 idiomas para transcripción/traducción:
- Español (es), Inglés (en), Francés (fr), Alemán (de), Italiano (it), Portugués (pt)
- Japonés (ja), Chino (zh), Coreano (ko), Ruso (ru), Árabe (ar)
- Hindi (hi), Turco (tr), Polaco (pl), Holandés (nl), Sueco (sv)

## Formatos de Audio Soportados

`.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.webm`, `.mp4`, `.wma`

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'whisperx'"
```bash
pip install git+https://github.com/m-bain/whisperx.git
```

### Error: "RuntimeError: CUDA not available"
No es un error crítico. El backend cae automáticamente a CPU con cuantización int8.

### Error: "FileNotFoundError: ffmpeg"
```bash
ffmpeg -version  # Verificar instalación
```

### Error: "espeak not installed on your system"
Instalar espeak-ng y asegurarse de que esté en PATH. En Windows puede ser necesario reiniciar la terminal.

### Error: "Supabase connection refused"
- Si usas Supabase local: ejecutar `supabase start`
- Verificar URLs y keys en `.env`
- Verificar migraciones: `supabase db reset` (local) o `supabase db push` (cloud)

### Error: "Sin créditos en ElevenLabs"
Tu cuenta de ElevenLabs se quedó sin créditos. Recarga en https://elevenlabs.io/subscription.

## Créditos

- **WhisperX**: https://github.com/m-bain/whisperx
- **Anthropic Claude**: https://www.anthropic.com
- **ElevenLabs**: https://elevenlabs.io
- **Supabase**: https://supabase.com
- **phonemizer**: https://github.com/bootphon/phonemizer
