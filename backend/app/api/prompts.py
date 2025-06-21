from fastapi import APIRouter, HTTPException
from app.models.prompt import PromptRequest, PromptImproveResponse, CodeGenerationRequest, CodeGenerationResponse
from app.services.prompt_improver import PromptImprover
from app.services.code_generator import ManimCodeGenerator

router = APIRouter()
prompt_improver = PromptImprover()
code_generator = ManimCodeGenerator()

@router.post("/improve", response_model=PromptImproveResponse)
async def improve_prompt(request: PromptRequest):
    """Improve user prompt for better Manim code generation"""
    try:
        result = await prompt_improver.improve_prompt(request.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error improving prompt: {str(e)}")

@router.post("/generate-code", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest):
    """Generate Manim code from improved prompt"""
    try:
        result = await code_generator.generate_code(
            request.improved_prompt,
            request.scene_name or "MainScene"
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating code: {str(e)}")