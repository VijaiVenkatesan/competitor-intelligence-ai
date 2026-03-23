from agents.base_agent import BaseAgent
from typing import Dict, Any
from utils.logger import logger


class FinancialAgent(BaseAgent):
    """Agent for financial analysis"""
    
    def __init__(self):
        super().__init__("FinancialAgent")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial data"""
        
        await self._log_execution(context)
        company_name = context.get('company_name')
        
        try:
            # For MVP: Use LLM general knowledge
            # In production: Integrate SEC API, Crunchbase, etc.
            
            prompt = f"""Provide financial analysis for {company_name} based on public knowledge.

Include:
1. Company type (public/private)
2. Estimated funding/revenue (if known)
3. Recent funding rounds (if any)
4. Growth stage (early/growth/mature)
5. Financial health assessment
6. Key investors (if known)

Return as JSON with fields: company_type, funding_estimate, growth_stage, health_score (0-100), assessment"""

            response = await self.llm.generate(
                prompt=prompt,
                system_prompt="You are a financial analyst. Provide realistic estimates based on publicly known information.",
                temperature=0.3,
                json_mode=True
            )
            
            import json
            financial_data = json.loads(response)
            
            return self._create_result(True, financial_data)
            
        except Exception as e:
            logger.error(f"Financial analysis failed: {e}")
            return self._create_result(
                True,
                {
                    "company_type": "Unknown",
                    "health_score": 50,
                    "assessment": "Limited financial data available"
                }
            )
