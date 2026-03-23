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
    Simplified orchestrator for Streamlit Cloud
    Runs agents sequentially to avoid resource limits
    """
    
    logger.info(f"Starting research for {company_name}")
    
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
        
        # Step 1: Web Research (20%)
        if progress_callback:
            progress_callback(10, "Starting web research...")
        
        web_result = await web_agent.execute({'company_name': company_name})
        result['web_research'] = web_result
        
        website_url = web_result.get('metadata', {}).get('website') if web_result.get('success') else None
        
        if progress_callback:
            progress_callback(20, "Web research complete")
        
        # Step 2: Social Media (40%)
        if progress_callback:
            progress_callback(30, "Analyzing social media...")
        
        social_result = await social_agent.execute({
            'company_name': company_name,
            'website_url': website_url
        })
        result['social_media'] = social_result
        
        if progress_callback:
            progress_callback(40, "Social media analysis complete")
        
        # Step 3: Financial (60%)
        if progress_callback:
            progress_callback(50, "Analyzing financials...")
        
        financial_result = await financial_agent.execute({
            'company_name': company_name
        })
        result['financial'] = financial_result
        
        if progress_callback:
            progress_callback(60, "Financial analysis complete")
        
        # Step 4: Product (80%)
        if progress_callback:
            progress_callback(70, "Analyzing product...")
        
        product_result = await product_agent.execute({
            'company_name': company_name,
            'website_url': website_url
        })
        result['product'] = product_result
        
        if progress_callback:
            progress_callback(80, "Product analysis complete")
        
        # Step 5: Synthesis (100%)
        if progress_callback:
            progress_callback(90, "Synthesizing insights...")
        
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
        
        if progress_callback:
            progress_callback(100, "Complete!")
        
        logger.info(f"Research complete for {company_name}")
        
        return result
        
    except Exception as e:
        logger.error(f"Research failed: {e}")
        raise
