from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PromptRequest(BaseModel):
    prompt: str
    user_id: Optional[str] = None

class PromptImproveResponse(BaseModel):
    original_prompt: str
    improved_prompt: str
    suggestions: list[str]

class CodeGenerationRequest(BaseModel):
    improved_prompt: str
    scene_name: Optional[str] = "MainScene"

class CodeGenerationResponse(BaseModel):
    code: str
    scene_name: str
    estimated_render_time: Optional[int] = None

class RenderRequest(BaseModel):
    code: str
    scene_name: Optional[str] = "MainScene"
    quality: Optional[str] = "medium"  # low, medium, high

class RenderResponse(BaseModel):
    success: bool
    video_url: Optional[str] = None
    file_id: Optional[str] = None
    error: Optional[str] = None
    render_time: Optional[float] = None