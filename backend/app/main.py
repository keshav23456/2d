from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from pathlib import Path

from app.config import settings
from app.api import prompts, manim

# Create FastAPI app
app = FastAPI(title="Manim Prompt-to-Code API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create output directories
os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
os.makedirs(f"{settings.LOCAL_STORAGE_PATH}/videos", exist_ok=True)
os.makedirs(f"{settings.LOCAL_STORAGE_PATH}/temp", exist_ok=True)
os.makedirs(f"{settings.LOCAL_STORAGE_PATH}/logs", exist_ok=True)

# Mount static files for video serving
app.mount("/videos", StaticFiles(directory=f"{settings.LOCAL_STORAGE_PATH}/videos"), name="videos")

# Include routers
app.include_router(prompts.router, prefix="/api/prompts", tags=["prompts"])
app.include_router(manim.router, prefix="/api/manim", tags=["manim"])

@app.get("/")
async def root():
    return {"message": "Manim Prompt-to-Code API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)