from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models import TranslateRequest
from services.translation import translate_segments
from services.supabase_client import get_supabase_client

router = APIRouter()


class TranslateRequestWithProject(TranslateRequest):
    project_id: Optional[str] = None


@router.post("/translate")
async def translate(req: TranslateRequestWithProject):
    try:
        translated = translate_segments(
            req.segments, req.source_language, req.target_language
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    # Save to database if project_id provided
    if req.project_id:
        supabase = get_supabase_client()

        translation_data = {
            "project_id": req.project_id,
            "segments_json": translated,
            "target_language": req.target_language,
            "source_language": req.source_language or "unknown",
        }
        supabase.table("translations").insert(translation_data).execute()

        # Update project status
        supabase.table("projects").update({"status": "translated"}).eq("id", req.project_id).execute()

    return {"segments": translated, "language": req.target_language}
