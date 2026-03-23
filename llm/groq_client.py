from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
from utils.config import settings
from utils.logger import logger
import json
from typing import Dict, Any
import os


class GroqClient:
    """Multi-model Groq client with TRUE optimization across different models"""
    
    # Real multi-model strategy using DIFFERENT models
    MODELS = {
        # Auto-optimize: Use optimal model per task type
        "auto": {
            "fast": "llama-3.1-8b-instant",          # ⚡ 10x faster for simple tasks
            "smart": "llama-3.3-70b-versatile",      # 🧠 Best for complex reasoning
            "structured": "llama-3.3-70b-versatile", # 📊 Most reliable for JSON
            "long": "mixtral-8x7b-32768",            # 📚 32K context window
        },
        
        # Single model strategies (user forces one model for all tasks)
        "llama-3.3-70b": "llama-3.3-70b-versatile",  # Best overall quality
        "llama-3.1-8b": "llama-3.1-8b-instant",      # Fastest
        "mixtral-8x7b": "mixtral-8x7b-32768",        # Long context alternative
        "gemma-7b": "gemma-7b-it",                   # Google's model
    }
    
    def __init__(self, strategy: str = "auto"):
        api_key = os.getenv("GROQ_API_KEY") or settings.groq_api_key
        if not api_key:
            raise ValueError("GROQ_API_KEY not found")
        
        self.client = Groq(api_key=api_key)
        self.strategy = strategy
        self.max_tokens = 8000
        
        logger.info(f"🤖 Initialized GroqClient with strategy: {strategy}")
    
    def get_model(self, task_type: str = "fast") -> str:
        """
        Get model based on strategy and task type
        
        Args:
            task_type: "fast", "smart", "structured", or "long"
        
        Returns:
            Model identifier string
        """
        
        if self.strategy == "auto":
            # Use optimal model per task
            model = self.MODELS["auto"].get(task_type, self.MODELS["auto"]["fast"])
            logger.debug(f"Auto-selected {model} for {task_type} task")
            return model
        else:
            # Use single selected model for all tasks
            model = self.MODELS.get(self.strategy, "llama-3.3-70b-versatile")
            logger.debug(f"Using forced model {model} (strategy: {self.strategy})")
            return model
    
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
        """Generate completion with automatic model selection"""
        
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
            logger.info(f"✅ Generated {len(content)} chars using {model} ({task_type} task)")
            
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
        """Generate structured JSON output"""
        
        enhanced_system = f"""{system_prompt}

You must respond with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Ensure all required fields are present and properly formatted."""
        
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
            return {"error": "Parse failed", "raw": response[:500]}


# Will be initialized with strategy in orchestrator
groq_client = None
