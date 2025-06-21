import google.generativeai as genai
from app.config import settings
from app.models.prompt import CodeGenerationResponse

class ManimCodeGenerator:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    async def generate_code(self, improved_prompt: str, scene_name: str = "MainScene") -> CodeGenerationResponse:
        """Generate Manim code from improved prompt"""
        
        if not self.model:
            return self._fallback_code_generation(improved_prompt, scene_name)
        
        code_prompt = f"""Convert this prompt into working Manim Python code.

Prompt: {improved_prompt}

Requirements:
1. Import necessary Manim modules
2. Create a Scene class named '{scene_name}'
3. Implement the construct() method
4. Use appropriate Manim objects and animations
5. Add comments explaining each step
6. Ensure the code is syntactically correct
7. Use proper animation timing

Return ONLY the Python code without any explanations or markdown formatting:"""
        
        try:
            response = self.model.generate_content(code_prompt)
            code = response.text.strip()
            
            # Clean up the code (remove markdown formatting if present)
            if code.startswith("```python"):
                code = code[9:]
            if code.endswith("```"):
                code = code[:-3]
            
            code = code.strip()
            
            # Ensure proper imports
            if "from manim import *" not in code:
                code = "from manim import *\n\n" + code
            
            return CodeGenerationResponse(
                code=code,
                scene_name=scene_name,
                estimated_render_time=self._estimate_render_time(code)
            )
            
        except Exception as e:
            print(f"Error generating code: {e}")
            return self._fallback_code_generation(improved_prompt, scene_name)
    
    def _estimate_render_time(self, code: str) -> int:
        """Estimate rendering time based on code complexity"""
        # Simple heuristic based on code length and complexity
        lines = len(code.split('\n'))
        animations = code.count('play(')
        objects = code.count('add(')
        
        base_time = 10  # seconds
        complexity_factor = (lines * 0.5) + (animations * 2) + (objects * 1)
        
        return int(base_time + complexity_factor)
    
    def _fallback_code_generation(self, prompt: str, scene_name: str) -> CodeGenerationResponse:
        """Fallback code generation without AI"""
        code = f'''from manim import *

class {scene_name}(Scene):
    def construct(self):
        # Generated from prompt: {prompt}
        
        # Create title
        title = Text("{prompt[:30]}...")
        title.to_edge(UP)
        self.play(Write(title))
        
        # Create a simple circle
        circle = Circle(radius=2, color=BLUE)
        self.play(Create(circle))
        
        # Add some movement
        self.play(circle.animate.shift(LEFT * 2))
        self.play(circle.animate.shift(RIGHT * 4))
        self.play(circle.animate.shift(LEFT * 2))
        
        # Fade out
        self.play(FadeOut(circle), FadeOut(title))
'''
        
        return CodeGenerationResponse(
            code=code,
            scene_name=scene_name,
            estimated_render_time=30
        )