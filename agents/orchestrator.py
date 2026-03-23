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
    model_strategy: str = "auto",  # ✅ NEW PARAMETER
    progress_callback: Optional[Callable] = None
) -> dict:
    """
    Main orchestrator for competitive research
    
    Args:
        company_name: Company to research
        depth: Research depth (quick/standard/deep)
        model_strategy: Model selection strategy (auto/speed/quality/balanced)
        progress_callback: Progress update function
    """
    
    logger.info(f"🚀 Starting research for: {company_name} (Strategy: {model_strategy})")
    
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
        # Initialize agents with model strategy
        web_agent = WebResearchAgent()
        social_agent = SocialMediaAgent()
        financial_agent = FinancialAgent()
        product_agent = ProductAgent()
        synthesis_agent = SynthesisAgent()
        
        # Set model strategy for each agent
        _apply_model_strategy(
            model_strategy,
            [web_agent, social_agent, financial_agent, product_agent, synthesis_agent]
        )
        
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


def _apply_model_strategy(strategy: str, agents: list):
    """Apply model strategy to all agents"""
    
    # Map UI strategy to model preferences
    strategy_map = {
        "auto": "auto",           # Each agent uses optimal model
        "speed": "fast",          # All agents use fast model
        "quality": "smart",       # All agents use smart model
        "balanced": "fast"        # All agents use balanced model
    }
    
    model_pref = strategy_map.get(strategy, "auto")
    
    if model_pref == "auto":
        # Keep default behavior (already optimized per agent)
        logger.info("🎯 Using auto-optimized model selection")
        return
    
    # Override all agents to use same model
    for agent in agents:
        agent.preferred_model = model_pref
        logger.info(f"📝 Set {agent.name} to use '{model_pref}' model")
