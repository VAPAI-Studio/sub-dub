from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from models import DubRequest
from services.tts import list_voices, generate_dub
from services.supabase_client import get_supabase_client

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


@router.post("/dub")
async def dub(req: DubRequestWithProject):
    if not req.segments:
        raise HTTPException(400, "No hay segmentos para generar doblaje")

    try:
        audio_output = generate_dub(
            req.segments, req.voice_map, req.default_voice_id, req.target_language
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    # Save to database if project_id provided
    if req.project_id:
        # Read audio bytes
        audio_bytes = audio_output.read()
        audio_output.seek(0)  # Reset for streaming response

        supabase = get_supabase_client()

        # TODO: Upload to Supabase Storage
        # For now, save metadata only
        dub_data = {
            "project_id": req.project_id,
            "audio_url": "local://temp",  # Placeholder
            "voice_map_json": req.voice_map,
        }
        supabase.table("dubs").insert(dub_data).execute()

        # Update project status
        supabase.table("projects").update({"status": "dubbed"}).eq("id", req.project_id).execute()

    return StreamingResponse(
        audio_output,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=dub.mp3"},
    )
