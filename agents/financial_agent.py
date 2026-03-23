from agents.base_agent import BaseAgent
from typing import Dict, Any
from utils.logger import logger
import json


class FinancialAgent(BaseAgent):
    """Financial analysis agent"""
    
    def __init__(self):
        super().__init__("FinancialAgent")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await self._log_execution(context)
        company_name = context.get('company_name')
        
        try:
            prompt = f"""Provide financial analysis for {company_name} based on publicly available knowledge.

Return JSON with these exact fields:
- company_type: "public" or "private"
- funding_estimate: funding amount string (e.g., "$100M Series C") or "Unknown"
- growth_stage: "early", "growth", or "mature"
- health_score: integer 0-100
- assessment: 2-3 sentence financial summary
- key_investors: list of investor names or empty list"""

            response = await self.llm.generate(
                prompt=prompt,
                system_prompt="You are a financial analyst. Provide realistic estimates based on publicly known information. Always return valid JSON.",
                temperature=0.3,
                json_mode=True,
                task_type="fast"
            )
            
            financial_data = json.loads(response)
            return self._create_result(True, financial_data)
            
        except Exception as e:
            logger.error(f"❌ Financial analysis failed: {e}")
            return self._create_result(
                True,
                {
                    "company_type": "Unknown",
                    "funding_estimate": "Unknown",
                    "growth_stage": "Unknown",
                    "health_score": 50,
                    "assessment": "Limited financial data available for analysis.",
                    "key_investors": []
                }
            )
