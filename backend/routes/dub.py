import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, RedirectResponse
from pydantic import BaseModel

from models import DubRequest
from services.tts import list_voices, list_library_voices, generate_dub
from services.supabase_client import get_supabase_client, upload_file, delete_file, get_public_url

router = APIRouter()


class DubRequestWithProject(DubRequest):
    project_id: Optional[str] = None


@router.get("/voices")
async def get_voices():
    try:
        voices = list_voices()
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"voices": voices}


@router.get("/voices/library")
async def get_library_voices(lang: str = Query(None)):
    try:
        voices = list_library_voices(language=lang)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"voices": voices}


@router.post("/dub")
async def dub(req: DubRequestWithProject):
    if not req.segments:
        raise HTTPException(400, "No hay segmentos para generar doblaje")

    try:
        audio_output = generate_dub(
            req.segments, req.voice_map, req.default_voice_id, req.target_language, req.source_language, req.timing_mode
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    # Save to storage and database if project_id provided
    if req.project_id:
        audio_bytes = audio_output.read()
        audio_output.seek(0)

        supabase = get_supabase_client()
        target_lang = req.target_language or "unknown"

        # Delete previous dub for this specific language
        existing = supabase.table("dubs").select("id, audio_url") \
            .eq("project_id", req.project_id) \
            .eq("target_language", target_lang).execute()
        if existing.data:
            for dub_record in existing.data:
                old_path = dub_record.get("audio_url", "")
                if old_path:
                    delete_file("audio-dubs", old_path)
            supabase.table("dubs").delete() \
                .eq("project_id", req.project_id) \
                .eq("target_language", target_lang).execute()

        # Upload to Supabase Storage
        storage_path = f"{req.project_id}/{target_lang}/{uuid.uuid4().hex[:8]}.mp3"
        upload_file("audio-dubs", storage_path, audio_bytes)

        # Save to database
        dub_data = {
            "project_id": req.project_id,
            "audio_url": storage_path,
            "voice_map_json": req.voice_map,
            "target_language": target_lang,
        }
        supabase.table("dubs").insert(dub_data).execute()

        # Update project status
        supabase.table("projects").update({"status": "dubbed"}).eq("id", req.project_id).execute()

    return StreamingResponse(
        audio_output,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=dub.mp3"},
    )


@router.get("/projects/{project_id}/dub-audio")
def get_dub_audio(project_id: str, lang: str = Query(...)):
    """Serve the dub audio file via Supabase Storage public URL"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("dubs").select("*") \
            .eq("project_id", project_id) \
            .eq("target_language", lang).execute()

        if not response.data:
            raise HTTPException(404, "No dub found for this project/language")

        dub = response.data[0]
        storage_path = dub["audio_url"]

        url = get_public_url("audio-dubs", storage_path)
        return RedirectResponse(url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
