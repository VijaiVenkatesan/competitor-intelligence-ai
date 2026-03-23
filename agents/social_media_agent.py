from agents.base_agent import BaseAgent
from typing import Dict, Any
from utils.logger import logger
import httpx
from llm.prompts import SOCIAL_MEDIA_ANALYSIS_PROMPT, SOCIAL_SENTIMENT_SCHEMA


class SocialMediaAgent(BaseAgent):
    """Social media analysis agent"""
    
    def __init__(self):
        super().__init__("SocialMediaAgent")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await self._log_execution(context)
        company_name = context.get('company_name')
        
        try:
            # Gather data from HackerNews
            hn_data = await self._analyze_hackernews(company_name)
            
            # ✅ FIX: Properly structure social_data
            social_data = {
                'hackernews': hn_data,
                'company_name': company_name
            }
            
            # Synthesize
            synthesis = await self._synthesize(company_name, social_data)
            
            return self._create_result(True, synthesis)
            
        except Exception as e:
            logger.error(f"❌ Social media analysis failed: {e}")
            return self._create_result(
                True,
                {
                    "overall_sentiment": "neutral",
                    "sentiment_score": 50,
                    "key_themes": ["Limited data available"],
                    "positive_feedback": [],
                    "negative_feedback": [],
                    "trending_topics": []
                }
            )
    
    async def _analyze_hackernews(self, company_name: str) -> Dict:
        url = "https://hn.algolia.com/api/v1/search"
        params = {'query': company_name, 'tags': 'story', 'hitsPerPage': 5}
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    hits = data.get('hits', [])
                    
                    return {
                        'mentions_count': len(hits),
                        'mentions': [{'title': h.get('title', ''), 'points': h.get('points', 0)} for h in hits],
                        'found': True
                    }
        except Exception as e:
            logger.warning(f"⚠️ HackerNews failed: {e}")
        
        return {'found': False, 'mentions_count': 0, 'mentions': []}
    
    async def _synthesize(self, company_name: str, social_data: Dict) -> Dict:
        prompt = SOCIAL_MEDIA_ANALYSIS_PROMPT.format(company_name=company_name)
        prompt += f"\n\nCollected Data:\n{str(social_data)[:2000]}"
        
        try:
            return await self.llm.generate_structured(
                prompt=prompt,
                system_prompt="Analyze social media presence and sentiment.",
                schema=SOCIAL_SENTIMENT_SCHEMA,
                task_type="fast"
            )
        except Exception as e:
            logger.error(f"❌ Social synthesis failed: {e}")
            return {
                "overall_sentiment": "neutral",
                "sentiment_score": 50,
                "key_themes": ["Analysis unavailable"],
                "positive_feedback": [],
                "negative_feedback": [],
                "trending_topics": []
            }
