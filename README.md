# SUB-DUB - Subtitles & Dubbing Tool

Herramienta web para generar subtítulos y doblaje desde archivos de audio/video. El flujo de trabajo es: **subir audio → transcribir → traducir → doblar con voces sintéticas**.

## 🚀 Características

- **Transcripción (ASR)**: WhisperX para transcribir audio a texto con marcas de tiempo
- **Traducción**: Claude AI para traducir subtítulos manteniendo la estructura temporal
- **Doblaje (TTS)**: ElevenLabs para generar voces sintéticas con mapeo de hablantes
- **Persistencia**: Supabase (PostgreSQL) para guardar proyectos y datos relacionados

## 📋 Requisitos Previos

- **Python 3.10+** (para backend)
- **Node.js 18+** y npm (para frontend)
- **FFmpeg** instalado y en PATH (requerido por pydub)
- **Supabase CLI** (opcional, para desarrollo local)
- GPU NVIDIA con CUDA (opcional, mejora rendimiento de transcripción)

## 🔑 API Keys Necesarias

Necesitarás obtener las siguientes claves:

1. **Hugging Face Token**: https://huggingface.co/settings/tokens (para diarización de hablantes)
2. **Anthropic API Key**: https://console.anthropic.com/ (para traducción con Claude)
3. **ElevenLabs API Key**: https://elevenlabs.io/app/settings/api-keys (para TTS)
4. **Supabase URL + Key**: https://supabase.com/dashboard/project/_/settings/api (o local con CLI)

## 📦 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/sub-dub.git
cd sub-dub
```

### 2. Configurar Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar archivo de ejemplo y configurar variables
cp .env.example .env
# Editar .env con tus API keys
```

**Configurar `.env` del backend:**

```env
HF_TOKEN=tu_token_de_huggingface
ANTHROPIC_API_KEY=tu_api_key_de_anthropic
ELEVENLABS_API_KEY=tu_api_key_de_elevenlabs
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_KEY=tu_supabase_key
```

### 3. Configurar Frontend

```bash
cd ../frontend

# Instalar dependencias
npm install

# Copiar archivo de ejemplo y configurar variables
cp .env.example .env
# Editar .env con la URL de tu backend
```

**Configurar `.env` del frontend:**

```env
VITE_API_URL=http://localhost:8001
VITE_SUPABASE_URL=http://127.0.0.1:54321
VITE_SUPABASE_ANON_KEY=tu_supabase_anon_key
```

### 4. Configurar Base de Datos (Supabase)

**Opción A: Supabase Local (Recomendado para desarrollo)**

```bash
# Instalar Supabase CLI
npm install -g supabase

# Iniciar Supabase local (desde la raíz del proyecto)
cd ..
supabase start

# Copiar las credenciales que aparecen en la consola a tus archivos .env
# API URL: http://127.0.0.1:54321
# anon key: eyJ...

# Aplicar migraciones
supabase db push
```

**Opción B: Supabase Cloud**

1. Crear proyecto en https://supabase.com/dashboard
2. Ir a Settings → API y copiar URL + anon key
3. Ir a SQL Editor y ejecutar el contenido de `supabase/migrations/20260326000001_create_projects_schema.sql`

### 5. Instalar FFmpeg

**Windows:**
```bash
# Con chocolatey
choco install ffmpeg

# O descargar desde: https://ffmpeg.org/download.html
```

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

## 🏃 Ejecutar el Proyecto

### Backend

```bash
cd backend
# Activar entorno virtual si no está activo
# venv\Scripts\activate (Windows) o source venv/bin/activate (Mac/Linux)

uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

El backend estará disponible en: http://localhost:8001

### Frontend

```bash
cd frontend
npm run dev
```

El frontend estará disponible en: http://localhost:5173

## 📁 Estructura del Proyecto

```
sub-dub/
├── backend/              # FastAPI REST API
│   ├── routes/           # Endpoints (transcribe, translate, dub, projects)
│   ├── services/         # Lógica de negocio (ASR, translation, TTS, Supabase)
│   ├── models.py         # Esquemas Pydantic
│   ├── config.py         # Configuración (CUDA/CPU, formatos permitidos)
│   ├── main.py           # App FastAPI
│   └── requirements.txt
├── frontend/             # React 19 SPA (Vite)
│   ├── src/
│   │   ├── components/   # Componentes reutilizables
│   │   ├── pages/        # Páginas principales
│   │   ├── services/     # API clients
│   │   └── lib/          # Utilidades (supabaseClient)
│   └── package.json
├── supabase/
│   ├── config.toml       # Configuración Supabase
│   └── migrations/       # SQL migrations
└── audios/               # Archivos de audio de ejemplo (opcional)
```

## 🔧 API Endpoints

| Método | Endpoint           | Descripción                                    |
|--------|--------------------|------------------------------------------------|
| GET    | `/projects/`       | Listar todos los proyectos                     |
| POST   | `/projects/`       | Crear nuevo proyecto                           |
| GET    | `/projects/{id}`   | Obtener proyecto con datos relacionados        |
| PUT    | `/projects/{id}`   | Actualizar proyecto                            |
| DELETE | `/projects/{id}`   | Eliminar proyecto (cascada)                    |
| POST   | `/transcribe`      | Subir audio y transcribir                      |
| POST   | `/translate`       | Traducir segmentos a idioma destino            |
| GET    | `/voices`          | Listar voces disponibles de ElevenLabs         |
| POST   | `/dub`             | Generar audio doblado desde segmentos + voces  |

## 🎯 Flujo de Uso

1. **Crear proyecto** → POST `/projects/` con nombre
2. **Subir audio** → POST `/transcribe` con archivo de audio
3. **Traducir** → POST `/translate` con segmentos transcritos
4. **Doblar** → POST `/dub` con segmentos traducidos + mapeo de voces
5. **Descargar resultado** → Archivo MP3 generado

## 🌍 Idiomas Soportados

16 idiomas para transcripción/traducción:
- Español (es), Inglés (en), Francés (fr), Alemán (de), Italiano (it), Portugués (pt)
- Japonés (ja), Chino (zh), Coreano (ko), Ruso (ru), Árabe (ar)
- Hindi (hi), Turco (tr), Polaco (pl), Holandés (nl), Sueco (sv)

## 🎵 Formatos de Audio Soportados

`.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.webm`, `.mp4`, `.wma`

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'whisperx'"
```bash
# WhisperX requiere instalación manual:
pip install git+https://github.com/m-bain/whisperx.git
```

### Error: "RuntimeError: CUDA not available"
No es un error crítico. El backend caerá automáticamente a CPU con cuantización int8. Para mejor rendimiento, instala CUDA toolkit.

### Error: "FileNotFoundError: ffmpeg"
Asegúrate de tener FFmpeg instalado y en PATH. Verifica con:
```bash
ffmpeg -version
```

### Error: "Supabase connection refused"
- Si usas Supabase local, asegúrate de ejecutar `supabase start`
- Verifica que las URLs y keys en `.env` sean correctas
- Revisa que las migraciones se hayan aplicado: `supabase db push`

## 📝 Notas

- Los archivos subidos se guardan temporalmente en `backend/uploads/`
- La primera transcripción puede tardar más (descarga modelo WhisperX ~1GB)
- GPU recomendada para transcripción rápida, pero funciona en CPU
- Supabase local usa Docker, asegúrate de tenerlo instalado

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

MIT License - ver archivo LICENSE para más detalles.

## 🙏 Créditos

- **WhisperX**: https://github.com/m-bain/whisperx
- **Anthropic Claude**: https://www.anthropic.com
- **ElevenLabs**: https://elevenlabs.io
- **Supabase**: https://supabase.com
