import os
import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from app.config import settings

class LocalStorageManager:
    def __init__(self):
        self.base_path = Path(settings.LOCAL_STORAGE_PATH)
        self.videos_path = self.base_path / "videos"
        self.temp_path = self.base_path / "temp"
        self.logs_path = self.base_path / "logs"
        
        # Ensure directories exist
        for path in [self.videos_path, self.temp_path, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def save_code(self, code: str) -> tuple[str, str]:
        """Save Python code to temporary file"""
        file_id = str(uuid.uuid4())
        code_path = self.temp_path / f"{file_id}.py"
        
        with open(code_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        return str(code_path), file_id
    
    def get_video_path(self, file_id: str) -> str:
        """Get path for rendered video"""
        return str(self.videos_path / f"{file_id}.mp4")
    
    def video_exists(self, file_id: str) -> bool:
        """Check if video file exists"""
        return (self.videos_path / f"{file_id}.mp4").exists()
    
    def cleanup_temp_files(self, file_id: str):
        """Remove temporary files after rendering"""
        temp_code = self.temp_path / f"{file_id}.py"
        if temp_code.exists():
            temp_code.unlink()
    
    def list_videos(self) -> List[dict]:
        """List all rendered videos with metadata"""
        videos = []
        for video_file in self.videos_path.glob("*.mp4"):
            stat = video_file.stat()
            videos.append({
                "file_id": video_file.stem,
                "filename": video_file.name,
                "size": stat.st_size,
                "created": stat.st_ctime,
                "url": f"/videos/{video_file.name}"
            })
        return videos
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Remove files older than specified hours"""
        import time
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        for file_path in self.temp_path.glob("*"):
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()