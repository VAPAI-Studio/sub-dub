from typing import Optional
from datetime import datetime

from pydantic import BaseModel


# ===== Project Models =====
class ProjectCreate(BaseModel):
    name: str


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime
    updated_at: datetime


class ProjectDetail(ProjectResponse):
    """Project with all related data"""
    audio_file: Optional[dict] = None
    transcription: Optional[dict] = None
    translations: list[dict] = []
    dubs: list[dict] = []


# ===== Translation Models =====
class TranslateSegment(BaseModel):
    start: float
    end: float
    text: str
    speaker: Optional[str] = None


class TranslateRequest(BaseModel):
    segments: list[TranslateSegment]
    target_language: str
    source_language: Optional[str] = None


class DubSegment(BaseModel):
    start: float
    end: float
    text: str
    speaker: Optional[str] = None
    original_text: Optional[str] = None


class DubRequest(BaseModel):
    segments: list[DubSegment]
    voice_map: dict[str, str]
    default_voice_id: Optional[str] = None
    target_language: Optional[str] = None
    source_language: Optional[str] = None
    timing_mode: Optional[str] = "strict"  # "strict", "natural", "free"
