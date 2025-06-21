import subprocess
import asyncio
import time
from pathlib import Path
from app.config import settings
from app.utils.file_handler import LocalStorageManager
from app.models.prompt import RenderResponse

class ManimRunner:
    def __init__(self):
        self.storage = LocalStorageManager()
    
    async def render_animation(self, code: str, scene_name: str = "MainScene", quality: str = "medium") -> RenderResponse:
        """Render Manim code to video"""
        start_time = time.time()
        
        try:
            # Save code to temporary file
            code_path, file_id = self.storage.save_code(code)
            
            # Quality settings
            quality_flags = {
                "low": ["-ql"],
                "medium": ["-qm"],
                "high": ["-qh"]
            }
            
            # Prepare Manim command
            output_path = self.storage.videos_path
            cmd = [
                "manim",
                code_path,
                scene_name,
                *quality_flags.get(quality, ["-qm"]),
                "--output_file", f"{file_id}.mp4",
                "--media_dir", str(output_path.parent)
            ]
            
            # Run Manim with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(Path.cwd())
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=settings.MAX_RENDERING_TIME
                )
                
                render_time = time.time() - start_time
                
                if process.returncode == 0:
                    # Check if video was created
                    video_path = self.storage.get_video_path(file_id)
                    if self.storage.video_exists(file_id):
                        # Clean up temporary files
                        self.storage.cleanup_temp_files(file_id)
                        
                        return RenderResponse(
                            success=True,
                            video_url=f"/videos/{file_id}.mp4",
                            file_id=file_id,
                            render_time=render_time
                        )
                    else:
                        error_msg = "Video file was not created"
                        if stderr:
                            error_msg += f": {stderr.decode()}"
                        
                        return RenderResponse(
                            success=False,
                            error=error_msg
                        )
                else:
                    error_msg = f"Manim process failed with return code {process.returncode}"
                    if stderr:
                        error_msg += f": {stderr.decode()}"
                    
                    return RenderResponse(
                        success=False,
                        error=error_msg
                    )
                    
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return RenderResponse(
                    success=False,
                    error=f"Rendering timeout after {settings.MAX_RENDERING_TIME} seconds"
                )
                
        except Exception as e:
            return RenderResponse(
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
        finally:
            # Always try to cleanup
            try:
                self.storage.cleanup_temp_files(file_id)
            except:
                pass