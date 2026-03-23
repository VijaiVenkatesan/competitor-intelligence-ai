from agents.base_agent import BaseAgent
from typing import Dict, Any
from utils.logger import logger


class ProductAgent(BaseAgent):
    """Agent for product analysis"""
    
    def __init__(self):
        super().__init__("ProductAgent")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze product offering"""
        
        await self._log_execution(context)
        company_name = context.get('company_name')
        website_url = context.get('website_url')
        
        try:
            prompt = f"""Analyze the product/service of {company_name}.

Website: {website_url or 'Not available'}

Provide analysis on:
1. Core product/service offering
2. Key features (list 5-7)
3. Pricing strategy (freemium/subscription/enterprise/etc)
4. Target user persona
5. Key differentiators vs competitors
6. Product-market fit score (0-100)

Return as JSON with fields: core_offerings, key_features (array), pricing_strategy, target_persona, differentiators (array), product_market_fit_score"""

            # ✅ USE "structured" model for reliable product data extraction
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt="You are a product analyst. Provide realistic analysis based on known information.",
                temperature=0.4,
                json_mode=True,
                model_type="structured"  # ✅ Best for structured product data
            )
            
            import json
            product_data = json.loads(response)
            
            return self._create_result(True, product_data)
            
        except Exception as e:
            logger.error(f"❌ Product analysis failed: {e}")
            return self._create_result(
                True,
                {
                    "core_offerings": "Analysis unavailable",
                    "key_features": [],
                    "pricing_strategy": "Unknown",
                    "product_market_fit_score": 50
                }
            )
