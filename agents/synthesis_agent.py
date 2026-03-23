from agents.base_agent import BaseAgent
from typing import Dict, Any
from utils.logger import logger
from llm.prompts import SYNTHESIS_PROMPT, SYNTHESIS_SCHEMA
import json


class SynthesisAgent(BaseAgent):
    """Synthesis agent - combines all research into final report"""
    
    def __init__(self):
        super().__init__("SynthesisAgent")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await self._log_execution(context)
        company_name = context.get('company_name')
        agent_outputs = context.get('agent_outputs', {})
        
        try:
            outputs_summary = self._format_outputs(agent_outputs)
            synthesis = await self._generate_synthesis(company_name, outputs_summary)
            return self._create_result(True, synthesis)
            
        except Exception as e:
            logger.error(f"❌ Synthesis failed: {e}")
            return self._create_result(True, self._fallback(company_name))
    
    def _format_outputs(self, outputs: Dict) -> str:
        formatted = []
        for name, output in outputs.items():
            if output.get('success') and output.get('data'):
                formatted.append(f"=== {name} ===")
                formatted.append(json.dumps(output.get('data', {}), indent=2)[:1500])
                formatted.append("")
        return "\n\n".join(formatted)
    
    async def _generate_synthesis(self, company_name: str, outputs: str) -> Dict:
        prompt = SYNTHESIS_PROMPT.format(
            company_name=company_name,
            agent_outputs=outputs[:8000]
        )
        
        return await self.llm.generate_structured(
            prompt=prompt,
            system_prompt="You are a senior strategy consultant. Provide comprehensive, actionable analysis. Always return valid JSON.",
            schema=SYNTHESIS_SCHEMA,
            task_type="smart"
        )
    
    def _fallback(self, company_name: str) -> Dict:
        return {
            "executive_summary": f"Analysis for {company_name} completed with limited data available.",
            "company_overview": {
                "background": "Information limited",
                "size_and_scale": "Unknown",
                "market_position": "Requires further research"
            },
            "swot_analysis": {
                "strengths": ["Unable to determine - limited data"],
                "weaknesses": ["Unable to determine - limited data"],
                "opportunities": ["Further research recommended"],
                "threats": ["Unable to determine - limited data"]
            },
            "product_analysis": {
                "core_offerings": "Unknown",
                "pricing_strategy": "Unknown",
                "differentiators": [],
                "product_market_fit_score": 50
            },
            "financial_health": {
                "status": "Unknown",
                "growth_trajectory": "Unknown",
                "health_score": 50
            },
            "strategic_recommendations": [
                "Conduct more detailed research",
                "Verify information through official sources",
                "Consider reaching out to company directly"
            ],
            "competitive_score": 50
        }
