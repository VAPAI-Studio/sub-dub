import os
import uuid

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse
from typing import List

from models import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetail
from config import ALLOWED_EXTENSIONS
from services.supabase_client import get_supabase_client, upload_file, delete_file, get_public_url

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectResponse])
def get_projects():
    """Get all projects"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("projects").select("*").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate):
    """Create a new project"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("projects").insert({"name": project.name}).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create project")

        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: str):
    """Get project with all related data"""
    try:
        supabase = get_supabase_client()

        project_response = supabase.table("projects").select("*").eq("id", project_id).execute()

        if not project_response.data:
            raise HTTPException(status_code=404, detail="Project not found")

        project = project_response.data[0]

        audio_response = supabase.table("audio_files").select("*").eq("project_id", project_id).execute()
        transcription_response = supabase.table("transcriptions").select("*").eq("project_id", project_id).execute()
        translation_response = supabase.table("translations").select("*").eq("project_id", project_id).execute()
        dub_response = supabase.table("dubs").select("*").eq("project_id", project_id).execute()

        return {
            **project,
            "audio_file": audio_response.data[0] if audio_response.data else None,
            "transcription": transcription_response.data[0] if transcription_response.data else None,
            "translations": translation_response.data,
            "dubs": dub_response.data,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/upload-audio")
async def upload_audio(project_id: str, file: UploadFile = File(...)):
    """Upload audio file to a project (replaces existing)"""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Formato no soportado: {ext}")

    try:
        supabase = get_supabase_client()

        # Check project exists
        project_response = supabase.table("projects").select("id").eq("id", project_id).execute()
        if not project_response.data:
            raise HTTPException(404, "Project not found")

        # Delete existing audio file for this project (replace)
        existing = supabase.table("audio_files").select("file_url").eq("project_id", project_id).execute()
        if existing.data:
            old_path = existing.data[0].get("file_url", "")
            if old_path:
                delete_file("audio-inputs", old_path)
            supabase.table("audio_files").delete().eq("project_id", project_id).execute()

        # Upload to Supabase Storage
        content = await file.read()
        storage_path = f"{project_id}/{uuid.uuid4().hex[:8]}{ext}"
        upload_file("audio-inputs", storage_path, content)

        # Save to database
        audio_data = {
            "project_id": project_id,
            "file_url": storage_path,
            "original_filename": file.filename,
        }
        result = supabase.table("audio_files").insert(audio_data).execute()

        return {
            "message": "Audio uploaded",
            "audio_file": result.data[0] if result.data else audio_data,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/audio")
def get_project_audio(project_id: str):
    """Serve the audio file for a project via Supabase Storage public URL"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("audio_files").select("*").eq("project_id", project_id).execute()

        if not response.data:
            raise HTTPException(404, "No audio file for this project")

        audio = response.data[0]
        storage_path = audio["file_url"]

        url = get_public_url("audio-inputs", storage_path)
        return RedirectResponse(url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: str, project: ProjectUpdate):
    """Update project"""
    try:
        supabase = get_supabase_client()

        update_data = project.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        response = supabase.table("projects").update(update_data).eq("id", project_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Project not found")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}")
def delete_project(project_id: str):
    """Delete project (cascades to all related data)"""
    try:
        supabase = get_supabase_client()

        # Delete audio files from storage
        audio_response = supabase.table("audio_files").select("file_url").eq("project_id", project_id).execute()
        if audio_response.data:
            for audio in audio_response.data:
                delete_file("audio-inputs", audio.get("file_url", ""))

        # Delete dub files from storage
        dub_response = supabase.table("dubs").select("audio_url").eq("project_id", project_id).execute()
        if dub_response.data:
            for dub in dub_response.data:
                delete_file("audio-dubs", dub.get("audio_url", ""))

        response = supabase.table("projects").delete().eq("id", project_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Project not found")

        return {"message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
