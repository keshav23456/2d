import google.generativeai as genai
from app.config import settings
from app.models.prompt import PromptImproveResponse

class PromptImprover:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    async def improve_prompt(self, original_prompt: str) -> PromptImproveResponse:
        """Improve user prompt for better Manim code generation"""
        
        if not self.model:
            # Fallback improvement without AI
            return self._fallback_improvement(original_prompt)
        
        system_prompt = """You are a Manim animation expert. Your task is to improve user prompts for creating mathematical animations.

Given a user's prompt, provide:
1. An improved, detailed prompt that specifies:
   - Mathematical objects and their properties
   - Animation sequences and timing
   - Visual elements (colors, positions, styles)
   - Specific Manim objects to use

2. A list of 3-5 suggestions for making the animation more engaging

Original prompt: {prompt}

Respond in this format:
IMPROVED_PROMPT: [Your improved prompt here]
SUGGESTIONS:
- [Suggestion 1]
- [Suggestion 2]
- [Suggestion 3]
"""
        
        try:
            response = self.model.generate_content(
                system_prompt.format(prompt=original_prompt)
            )
            
            # Parse response
            content = response.text
            parts = content.split("SUGGESTIONS:")
            
            improved_prompt = parts[0].replace("IMPROVED_PROMPT:", "").strip()
            suggestions = []
            
            if len(parts) > 1:
                suggestion_lines = parts[1].strip().split('\n')
                suggestions = [line.strip('- ').strip() for line in suggestion_lines if line.strip()]
            
            return PromptImproveResponse(
                original_prompt=original_prompt,
                improved_prompt=improved_prompt,
                suggestions=suggestions
            )
            
        except Exception as e:
            print(f"Error improving prompt: {e}")
            return self._fallback_improvement(original_prompt)
    
    def _fallback_improvement(self, original_prompt: str) -> PromptImproveResponse:
        """Fallback improvement without AI"""
        improved_prompt = f"""Create a mathematical animation that shows: {original_prompt}

Use appropriate Manim objects like Circle, Square, Line, MathTex, Text.
Add smooth animations with transforms and movements.
Use different colors to distinguish elements.
Include proper timing and sequencing."""
        
        suggestions = [
            "Add mathematical formulas using MathTex",
            "Use different colors for different elements",
            "Include smooth transitions between scenes",
            "Add explanatory text labels",
            "Consider showing step-by-step progression"
        ]
        
        return PromptImproveResponse(
            original_prompt=original_prompt,
            improved_prompt=improved_prompt,
            suggestions=suggestions
        )