from fastapi import APIRouter, HTTPException
from app.models.prompt import RenderRequest, RenderResponse
from app.services.manim_runner import ManimRunner
from app.utils.file_handler import LocalStorageManager

router = APIRouter()
manim_runner = ManimRunner()
storage = LocalStorageManager()

@router.post("/render", response_model=RenderResponse)
async def render_animation(request: RenderRequest):
    """Render Manim code to video"""
    try:
        result = await manim_runner.render_animation(
            request.code,
            request.scene_name or "MainScene",
            request.quality or "medium"
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering animation: {str(e)}")

@router.get("/videos")
async def list_videos():
    """List all rendered videos"""
    try:
        videos = storage.list_videos()
        return {"videos": videos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing videos: {str(e)}")

@router.delete("/videos/{file_id}")
async def delete_video(file_id: str):
    """Delete a rendered video"""
    try:
        video_path = storage.get_video_path(file_id)
        if storage.video_exists(file_id):
            import os
            os.remove(video_path)
            return {"message": "Video deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Video not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting video: {str(e)}")