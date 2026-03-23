from agents.base_agent import BaseAgent
from typing import Dict, Any
from utils.logger import logger
import httpx
from llm.prompts import SOCIAL_MEDIA_ANALYSIS_PROMPT, SOCIAL_SENTIMENT_SCHEMA


class SocialMediaAgent(BaseAgent):
    """Agent for social media intelligence"""
    
    def __init__(self):
        super().__init__("SocialMediaAgent")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather social media intelligence"""
        
        await self._log_execution(context)
        company_name = context.get('company_name')
        
        try:
            social_data = {}
            
            reddit_data = await self._analyze_reddit(company_name)
            social_data['reddit'] = reddit_data
            
            hn_data = await self._analyze_hackernews(company_name)
            social_data['hackernews'] = hn_data
            
            # ✅ USE "fast" model for quick sentiment analysis
            synthesis = await self._synthesize_social_intelligence(
                company_name,
                social_data
            )
            
            return self._create_result(True, synthesis)
            
        except Exception as e:
            logger.error(f"❌ Social media analysis failed: {e}")
            return self._create_result(
                True,
                {
                    "overall_sentiment": "neutral",
                    "sentiment_score": 50,
                    "key_themes": ["Data not available"],
                    "note": f"Limited data: {str(e)}"
                }
            )
    
    async def _analyze_reddit(self, company_name: str) -> Dict[str, Any]:
        """Analyze Reddit mentions"""
        
        search_url = f"https://www.reddit.com/search.json?q={company_name}&limit=10"
        
        try:
            async with httpx.AsyncClient(
                timeout=10,
                headers={'User-Agent': 'CompetitorResearch/1.0'}
            ) as client:
                response = await client.get(search_url)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    mentions = []
                    for post in posts[:5]:
                        post_data = post.get('data', {})
                        mentions.append({
                            'title': post_data.get('title', ''),
                            'score': post_data.get('score', 0),
                            'num_comments': post_data.get('num_comments', 0)
                        })
                    
                    return {
                        'mentions_count': len(mentions),
                        'mentions': mentions,
                        'found': True
                    }
        except Exception as e:
            logger.warning(f"⚠️ Reddit analysis failed: {e}")
        
        return {'found': False, 'mentions_count': 0}
    
    async def _analyze_hackernews(self, company_name: str) -> Dict[str, Any]:
        """Analyze HackerNews mentions"""
        
        url = "https://hn.algolia.com/api/v1/search"
        params = {
            'query': company_name,
            'tags': 'story',
            'hitsPerPage': 5
        }
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    hits = data.get('hits', [])
                    
                    mentions = [{
                        'title': hit.get('title', ''),
                        'points': hit.get('points', 0),
                        'num_comments': hit.get('num_comments', 0)
                    } for hit in hits]
                    
                    return {
                        'mentions_count': len(mentions),
                        'mentions': mentions,
                        'found': True
                    }
        except Exception as e:
            logger.warning(f"⚠️ HackerNews analysis failed: {e}")
        
        return {'found': False, 'mentions_count': 0}
    
    async def _synthesize_social_intelligence(
        self,
        company_name: str,
        social_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use LLM to synthesize social media insights"""
        
        prompt = SOCIAL_MEDIA_ANALYSIS_PROMPT.format(
            company_name=company_name
        )
        prompt += f"\n\nCollected Data:\n{str(social_data)[:3000]}"
        
        try:
            # ✅ USE "fast" model - quick sentiment analysis
            synthesis = await self.llm.generate_structured(
                prompt=prompt,
                system_prompt="You are a social media analyst. If data is limited, provide general insights.",
                schema=SOCIAL_SENTIMENT_SCHEMA,
                model_type="fast"  # ✅ Optimized for speed
            )
            return synthesis
            
        except Exception as e:
            logger.error(f"❌ Social synthesis failed: {e}")
            return {
                "overall_sentiment": "neutral",
                "sentiment_score": 50,
                "key_themes": ["Limited social data"],
                "positive_feedback": [],
                "negative_feedback": [],
                "trending_topics": []
            }
