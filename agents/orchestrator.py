import asyncio
from typing import Callable, Optional
from agents.web_research_agent import WebResearchAgent
from agents.social_media_agent import SocialMediaAgent
from agents.financial_agent import FinancialAgent
from agents.product_agent import ProductAgent
from agents.synthesis_agent import SynthesisAgent
from utils.logger import logger


async def run_research(
    company_name: str,
    depth: str = "standard",
    progress_callback: Optional[Callable] = None
) -> dict:
    """
    Main orchestrator for competitive research
    Runs agents sequentially for Streamlit Cloud compatibility
    """
    
    logger.info(f"🚀 Starting research for: {company_name}")
    
    result = {
        'company_name': company_name,
        'depth': depth,
        'web_research': {},
        'social_media': {},
        'financial': {},
        'product': {},
        'synthesis': {}
    }
    
    try:
        # Initialize agents
        web_agent = WebResearchAgent()
        social_agent = SocialMediaAgent()
        financial_agent = FinancialAgent()
        product_agent = ProductAgent()
        synthesis_agent = SynthesisAgent()
        
        # Progress tracking helper
        def update_progress(pct: int, msg: str):
            logger.info(f"Progress: {pct}% - {msg}")
            if progress_callback:
                progress_callback(pct, msg)
        
        # STEP 1: Web Research (0-25%)
        update_progress(5, "🌐 Researching company website...")
        web_result = await web_agent.execute({'company_name': company_name})
        result['web_research'] = web_result
        
        website_url = None
        if web_result.get('success'):
            website_url = web_result.get('metadata', {}).get('website')
        
        update_progress(25, "✅ Web research complete")
        
        # STEP 2: Social Media (25-45%)
        update_progress(30, "📱 Analyzing social media presence...")
        social_result = await social_agent.execute({
            'company_name': company_name,
            'website_url': website_url
        })
        result['social_media'] = social_result
        update_progress(45, "✅ Social media analysis complete")
        
        # STEP 3: Financial (45-65%)
        update_progress(50, "💰 Gathering financial data...")
        financial_result = await financial_agent.execute({
            'company_name': company_name
        })
        result['financial'] = financial_result
        update_progress(65, "✅ Financial analysis complete")
        
        # STEP 4: Product (65-85%)
        update_progress(70, "🎨 Analyzing product offering...")
        product_result = await product_agent.execute({
            'company_name': company_name,
            'website_url': website_url
        })
        result['product'] = product_result
        update_progress(85, "✅ Product analysis complete")
        
        # STEP 5: Synthesis (85-100%)
        update_progress(90, "🧠 Synthesizing insights...")
        
        agent_outputs = {
            'web_research': web_result,
            'social_media': social_result,
            'financial': financial_result,
            'product': product_result
        }
        
        synthesis_result = await synthesis_agent.execute({
            'company_name': company_name,
            'agent_outputs': agent_outputs
        })
        
        result['synthesis'] = synthesis_result.get('data', {})
        
        update_progress(100, "✅ Research complete!")
        
        logger.info(f"✅ Research completed successfully for {company_name}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Research failed: {e}")
        raise
