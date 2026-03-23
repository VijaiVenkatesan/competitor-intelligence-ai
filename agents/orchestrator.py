import asyncio
from typing import Callable, Optional
from agents.web_research_agent import WebResearchAgent
from agents.social_media_agent import SocialMediaAgent
from agents.financial_agent import FinancialAgent
from agents.product_agent import ProductAgent
from agents.synthesis_agent import SynthesisAgent
from utils.logger import logger
from llm.groq_client import GroqClient
import llm.groq_client as groq_module


async def run_research(
    company_name: str,
    depth: str = "standard",
    model_strategy: str = "auto",  # ✅ User's model choice
    progress_callback: Optional[Callable] = None
) -> dict:
    """Main orchestrator with user-selectable model strategy"""
    
    logger.info(f"🚀 Research: {company_name} | Strategy: {model_strategy}")
    
    # ✅ Initialize LLM client with user's chosen strategy
    groq_module.groq_client = GroqClient(strategy=model_strategy)
    
    result = {
        'company_name': company_name,
        'depth': depth,
        'model_strategy': model_strategy,
        'web_research': {},
        'social_media': {},
        'financial': {},
        'product': {},
        'synthesis': {}
    }
    
    try:
        web_agent = WebResearchAgent()
        social_agent = SocialMediaAgent()
        financial_agent = FinancialAgent()
        product_agent = ProductAgent()
        synthesis_agent = SynthesisAgent()
        
        def update(pct: int, msg: str):
            logger.info(f"{pct}% - {msg}")
            if progress_callback:
                progress_callback(pct, msg)
        
        # Web Research
        update(5, "🌐 Researching website...")
        web_result = await web_agent.execute({'company_name': company_name})
        result['web_research'] = web_result
        website_url = web_result.get('metadata', {}).get('website') if web_result.get('success') else None
        update(25, "✅ Web complete")
        
        # Social
        update(30, "📱 Analyzing social...")
        social_result = await social_agent.execute({'company_name': company_name, 'website_url': website_url})
        result['social_media'] = social_result
        update(45, "✅ Social complete")
        
        # Financial
        update(50, "💰 Financial data...")
        financial_result = await financial_agent.execute({'company_name': company_name})
        result['financial'] = financial_result
        update(65, "✅ Financial complete")
        
        # Product
        update(70, "🎨 Product analysis...")
        product_result = await product_agent.execute({'company_name': company_name, 'website_url': website_url})
        result['product'] = product_result
        update(85, "✅ Product complete")
        
        # Synthesis
        update(90, "🧠 Synthesizing...")
        synthesis_result = await synthesis_agent.execute({
            'company_name': company_name,
            'agent_outputs': {
                'web_research': web_result,
                'social_media': social_result,
                'financial': financial_result,
                'product': product_result
            }
        })
        result['synthesis'] = synthesis_result.get('data', {})
        
        update(100, "✅ Complete!")
        
        logger.info(f"✅ Research completed for {company_name}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Research failed: {e}")
        raise
