from agents.base_agent import BaseAgent
from typing import Dict, Any
from utils.logger import logger
from llm.prompts import SYNTHESIS_PROMPT, SYNTHESIS_SCHEMA
import json


class SynthesisAgent(BaseAgent):
    """Agent for synthesizing all research into final report"""
    
    def __init__(self):
        super().__init__("SynthesisAgent")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize all agent outputs"""
        
        await self._log_execution(context)
        company_name = context.get('company_name')
        agent_outputs = context.get('agent_outputs', {})
        
        try:
            # Format agent outputs for LLM
            outputs_summary = self._format_agent_outputs(agent_outputs)
            
            # Generate synthesis
            synthesis = await self._generate_synthesis(
                company_name,
                outputs_summary
            )
            
            return self._create_result(True, synthesis)
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return self._create_result(
                True,
                self._create_fallback_synthesis(company_name)
            )
    
    def _format_agent_outputs(self, agent_outputs: Dict) -> str:
        """Format agent outputs for LLM"""
        
        formatted = []
        
        for agent_name, output in agent_outputs.items():
            if output.get('success'):
                formatted.append(f"=== {agent_name} ===")
                formatted.append(json.dumps(output.get('data', {}), indent=2)[:1500])
                formatted.append("")
        
        return "\n".join(formatted)
    
    async def _generate_synthesis(
        self,
        company_name: str,
        outputs_summary: str
    ) -> Dict[str, Any]:
        """Generate comprehensive synthesis"""
        
        prompt = SYNTHESIS_PROMPT.format(
            company_name=company_name,
            agent_outputs=outputs_summary[:8000]  # Token limit
        )
        
        synthesis = await self.llm.generate_structured(
            prompt=prompt,
            system_prompt="You are a senior strategy consultant. Provide comprehensive, actionable analysis.",
            schema=SYNTHESIS_SCHEMA
        )
        
        return synthesis
    
    def _create_fallback_synthesis(self, company_name: str) -> Dict[str, Any]:
        """Create minimal valid synthesis on error"""
        
        return {
            "executive_summary": f"Analysis for {company_name} completed with limited data.",
            "company_overview": {
                "background": "Data unavailable",
                "size_and_scale": "Unknown",
                "market_position": "Unknown"
            },
            "swot_analysis": {
                "strengths": ["Data collection in progress"],
                "weaknesses": ["Limited information available"],
                "opportunities": ["Further research needed"],
                "threats": ["Analysis incomplete"]
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
                "Conduct deeper research",
                "Verify data sources",
                "Update analysis with more information"
            ],
            "competitive_score": 50
        }
