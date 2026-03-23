from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
from utils.config import settings
from utils.logger import logger
import json
from typing import Optional, Dict, Any, List
import os
from collections import Counter


class GroqClient:
    """Enhanced Groq client with multi-model support for optimal results"""
    
    # Model configurations - All FREE on Groq!
    MODELS = {
        "fast": "llama-3.3-70b-versatile",          # Fast, balanced (DEFAULT)
        "smart": "llama-3.1-70b-specdec",           # Deep reasoning & analysis
        "long": "mixtral-8x7b-32768",               # Long context (32K tokens)
        "creative": "llama-3.3-70b-versatile",      # Creative synthesis
        "structured": "llama-3.3-70b-versatile",    # Reliable JSON output
    }
    
    def __init__(self, default_model: str = "fast"):
        api_key = os.getenv("GROQ_API_KEY") or settings.groq_api_key
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        
        self.client = Groq(api_key=api_key)
        self.default_model = self.MODELS.get(default_model, self.MODELS["fast"])
        self.max_tokens = 8000
    
    def get_model(self, model_type: str = "fast") -> str:
        """Get model name by type"""
        return self.MODELS.get(model_type, self.default_model)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful AI assistant.",
        temperature: float = 0.7,
        json_mode: bool = False,
        model_type: str = "fast"
    ) -> str:
        """Generate completion with retry logic and model selection"""
        
        model = self.get_model(model_type)
        
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
            logger.error(f"❌ Groq API error with {model}: {e}")
            raise
    
    async def generate_structured(
        self,
        prompt: str,
        system_prompt: str,
        schema: Dict[str, Any],
        model_type: str = "structured"
    ) -> Dict[str, Any]:
        """Generate structured JSON output with schema validation"""
        
        enhanced_system = f"""{system_prompt}

You must respond with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Ensure all required fields are present and properly formatted."""
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=enhanced_system,
            temperature=0.3,
            json_mode=True,
            model_type=model_type
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON: {e}")
            return {"error": "Failed to parse response", "raw": response[:500]}
    
    async def generate_with_fallback(
        self,
        prompt: str,
        system_prompt: str,
        primary_model: str = "fast",
        fallback_model: str = "smart",
        **kwargs
    ) -> str:
        """Try primary model, fallback to secondary if fails"""
        
        try:
            return await self.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                model_type=primary_model,
                **kwargs
            )
        except Exception as e:
            logger.warning(f"⚠️ Primary model {primary_model} failed, trying {fallback_model}")
            return await self.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                model_type=fallback_model,
                **kwargs
            )
    
    async def generate_with_ensemble(
        self,
        prompt: str,
        system_prompt: str,
        models: List[str] = ["fast", "smart"],
        **kwargs
    ) -> str:
        """Generate using multiple models and return consensus (advanced)"""
        
        results = []
        
        for model_type in models:
            try:
                result = await self.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model_type=model_type,
                    **kwargs
                )
                results.append(result)
                logger.info(f"✅ Ensemble: Got result from {model_type}")
            except Exception as e:
                logger.warning(f"⚠️ Ensemble: {model_type} failed: {e}")
        
        if not results:
            raise Exception("❌ All models failed in ensemble")
        
        # Return most common result (simple voting)
        if len(results) > 1:
            counter = Counter(results)
            most_common = counter.most_common(1)[0][0]
            logger.info(f"🎯 Ensemble: Using consensus result")
            return most_common
        
        return results[0]


# Singleton instance
groq_client = GroqClient()
