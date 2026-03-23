from agents.base_agent import BaseAgent
from typing import Dict, Any
from utils.logger import logger
import json


class ProductAgent(BaseAgent):
    """Product analysis agent"""
    
    def __init__(self):
        super().__init__("ProductAgent")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await self._log_execution(context)
        company_name = context.get('company_name')
        website_url = context.get('website_url')
        
        try:
            prompt = f"""Analyze the product/service offering of {company_name}.

Website: {website_url or 'Not available'}

Return JSON with these exact fields:
- core_offerings: string describing main product/service
- key_features: array of 5-7 key features
- pricing_strategy: one of "freemium", "subscription", "enterprise", "pay-per-use", "custom", or "unknown"
- target_persona: string describing ideal customer
- differentiators: array of 3-5 unique competitive advantages
- product_market_fit_score: integer 0-100"""

            response = await self.llm.generate(
                prompt=prompt,
                system_prompt="You are a product analyst. Provide realistic analysis based on known information. Always return valid JSON.",
                temperature=0.4,
                json_mode=True,
                task_type="structured"
            )
            
            product_data = json.loads(response)
            return self._create_result(True, product_data)
            
        except Exception as e:
            logger.error(f"❌ Product analysis failed: {e}")
            return self._create_result(
                True,
                {
                    "core_offerings": "Product analysis unavailable",
                    "key_features": [],
                    "pricing_strategy": "unknown",
                    "target_persona": "Unknown",
                    "differentiators": [],
                    "product_market_fit_score": 50
                }
            )
