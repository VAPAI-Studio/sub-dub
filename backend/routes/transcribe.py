import os
import uuid
import tempfile
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from config import ALLOWED_EXTENSIONS, VALID_MODELS
from services.asr import transcribe_audio, align_audio, diarize_audio, format_segments
from services.supabase_client import get_supabase_client, upload_file

router = APIRouter()


@router.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    model_size: str = Form("large-v2"),
    language: str = Form("auto"),
    task: str = Form("transcribe"),
    align: bool = Form(False),
    diarize: bool = Form(False),
    min_speakers: Optional[int] = Form(None),
    max_speakers: Optional[int] = Form(None),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Formato no soportado: {ext}")

    if task not in ("transcribe", "translate"):
        raise HTTPException(400, f"Tarea no válida: {task}")

    if model_size not in VALID_MODELS:
        raise HTTPException(400, f"Modelo no válido: {model_size}")

    # Save to temp file for WhisperX (needs local file path)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    file_path = temp_file.name
    try:
        content = await file.read()
        temp_file.write(content)
        temp_file.close()

        audio, result = transcribe_audio(file_path, model_size, language, task)
        detected_language = result.get("language", "unknown")

        if align or diarize:
            result = align_audio(audio, result)

        if diarize:
            try:
                result = diarize_audio(audio, result, min_speakers, max_speakers)
            except ValueError as e:
                raise HTTPException(400, str(e))

        segments = format_segments(result, include_words=(align or diarize))

        # Save to database and storage if project_id provided
        if project_id:
            supabase = get_supabase_client()

            # Upload audio to Supabase Storage
            storage_path = f"{project_id}/{uuid.uuid4().hex[:8]}{ext}"
            upload_file("audio-inputs", storage_path, content)

            # Check if audio_files already exists for this project (from upload-audio endpoint)
            existing = supabase.table("audio_files").select("id").eq("project_id", project_id).execute()
            if not existing.data:
                # Save audio file info only if not already uploaded
                audio_data = {
                    "project_id": project_id,
                    "file_url": storage_path,
                    "original_filename": file.filename,
                    "duration": segments[-1]["end"] if segments else None,
                }
                supabase.table("audio_files").insert(audio_data).execute()
            else:
                # Update duration on existing record
                supabase.table("audio_files").update({
                    "duration": segments[-1]["end"] if segments else None,
                }).eq("project_id", project_id).execute()

            # Save transcription (replace existing)
            existing_transcription = supabase.table("transcriptions").select("id").eq("project_id", project_id).execute()
            transcription_data = {
                "project_id": project_id,
                "segments_json": segments,
                "language": detected_language,
                "model": model_size,
                "options_json": {
                    "task": task,
                    "align": align,
                    "diarize": diarize,
                    "min_speakers": min_speakers,
                    "max_speakers": max_speakers,
                },
            }
            if existing_transcription.data:
                supabase.table("transcriptions").update(transcription_data) \
                    .eq("id", existing_transcription.data[0]["id"]).execute()
            else:
                supabase.table("transcriptions").insert(transcription_data).execute()

            # Update project status
            supabase.table("projects").update({"status": "transcribed"}).eq("id", project_id).execute()

        return {"segments": segments, "language": detected_language}
    finally:
        # Always clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)
