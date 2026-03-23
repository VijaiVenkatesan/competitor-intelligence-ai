from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
from utils.config import settings
from utils.logger import logger
import json
from typing import Dict, Any
import os


class GroqClient:
    """Multi-model Groq client with user-selectable models"""
    
    # All available models
    MODELS = {
        # Auto-optimize uses best per task
        "auto": {
            "fast": "llama-3.3-70b-versatile",
            "smart": "llama-3.3-70b-versatile",
            "structured": "llama-3.3-70b-versatile",
        },
        # Single model strategies
        "llama-3.3-fast": "llama-3.3-70b-versatile",
        "llama-3.3-quality": "llama-3.3-70b-versatile",
        "mixtral-8x7b": "mixtral-8x7b-32768",
    }
    
    def __init__(self, strategy: str = "auto"):
        api_key = os.getenv("GROQ_API_KEY") or settings.groq_api_key
        if not api_key:
            raise ValueError("GROQ_API_KEY not found")
        
        self.client = Groq(api_key=api_key)
        self.strategy = strategy
        self.max_tokens = 8000
    
    def get_model(self, task_type: str = "fast") -> str:
        """Get model based on strategy and task"""
        
        if self.strategy == "auto":
            # Use optimal model per task
            return self.MODELS["auto"].get(task_type, self.MODELS["auto"]["fast"])
        else:
            # Use single selected model
            return self.MODELS.get(self.strategy, "llama-3.3-70b-versatile")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful AI assistant.",
        temperature: float = 0.7,
        json_mode: bool = False,
        task_type: str = "fast"
    ) -> str:
        """Generate with automatic model selection"""
        
        model = self.get_model(task_type)
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"} if json_mode else {"type": "text"}
            )
            
            content = response.choices[0].message.content
            logger.info(f"✅ Generated {len(content)} chars using {model}")
            
            return content
            
        except Exception as e:
            logger.error(f"❌ Model {model} failed: {e}")
            raise
    
    async def generate_structured(
        self,
        prompt: str,
        system_prompt: str,
        schema: Dict[str, Any],
        task_type: str = "structured"
    ) -> Dict[str, Any]:
        """Generate structured JSON"""
        
        enhanced_system = f"""{system_prompt}

Respond with valid JSON matching this schema:
{json.dumps(schema, indent=2)}"""
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=enhanced_system,
            temperature=0.3,
            json_mode=True,
            task_type=task_type
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse failed: {e}")
            return {"error": "Parse failed"}


# Will be initialized with strategy in orchestrator
groq_client = None
