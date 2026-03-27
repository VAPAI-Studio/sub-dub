from fastapi import APIRouter, HTTPException
from typing import List

from models import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetail
from services.supabase_client import get_supabase_client

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

        # Get project
        project_response = supabase.table("projects").select("*").eq("id", project_id).execute()

        if not project_response.data:
            raise HTTPException(status_code=404, detail="Project not found")

        project = project_response.data[0]

        # Get related data
        audio_response = supabase.table("audio_files").select("*").eq("project_id", project_id).execute()
        transcription_response = supabase.table("transcriptions").select("*").eq("project_id", project_id).execute()
        translation_response = supabase.table("translations").select("*").eq("project_id", project_id).execute()
        dub_response = supabase.table("dubs").select("*").eq("project_id", project_id).execute()

        # Build response
        return {
            **project,
            "audio_file": audio_response.data[0] if audio_response.data else None,
            "transcription": transcription_response.data[0] if transcription_response.data else None,
            "translation": translation_response.data[0] if translation_response.data else None,
            "dub": dub_response.data[0] if dub_response.data else None,
        }
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
        response = supabase.table("projects").delete().eq("id", project_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Project not found")

        return {"message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
