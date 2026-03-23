from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
from utils.config import settings
from utils.logger import logger
import json
from typing import Optional, Dict, Any
import os


class GroqClient:
    """Wrapper for Groq API with retry logic"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY") or settings.groq_api_key
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-70b-versatile"
        self.max_tokens = 8000
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful AI assistant.",
        temperature: float = 0.7,
        json_mode: bool = False
    ) -> str:
        """Generate completion with retry logic"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"} if json_mode else {"type": "text"}
            )
            
            content = response.choices[0].message.content
            logger.info(f"Generated {len(content)} characters")
            
            return content
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise
    
    async def generate_structured(
        self,
        prompt: str,
        system_prompt: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate structured JSON output"""
        
        enhanced_system = f"""{system_prompt}

You must respond with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Ensure all required fields are present."""
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=enhanced_system,
            temperature=0.3,
            json_mode=True
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            # Return minimal valid response
            return {"error": "Failed to parse response", "raw": response[:500]}


# Singleton instance
groq_client = GroqClient()
