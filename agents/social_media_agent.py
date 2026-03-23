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
            
            # Synthesize with LLM
            synthesis = await self._synthesize(company_name, hn_data)
            
            return self._create_result(True, synthesis)
            
        except Exception as e:
            logger.error(f"❌ Social media analysis failed: {e}")
            # Return fallback data
            return self._create_result(
                True,
                {
                    "overall_sentiment": "neutral",
                    "sentiment_score": 50,
                    "key_themes": ["Limited social data available"],
                    "positive_feedback": [],
                    "negative_feedback": [],
                    "trending_topics": []
                }
            )
    
    async def _analyze_hackernews(self, company_name: str) -> Dict:
        """Fetch HackerNews mentions"""
        url = "https://hn.algolia.com/api/v1/search"
        params = {'query': company_name, 'tags': 'story', 'hitsPerPage': 5}
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    hits = data.get('hits', [])
                    
                    return {
                        'source': 'hackernews',
                        'mentions_count': len(hits),
                        'mentions': [
                            {
                                'title': h.get('title', ''),
                                'points': h.get('points', 0),
                                'comments': h.get('num_comments', 0)
                            } 
                            for h in hits
                        ],
                        'found': len(hits) > 0
                    }
        except Exception as e:
            logger.warning(f"⚠️ HackerNews fetch failed: {e}")
        
        return {
            'source': 'hackernews',
            'mentions_count': 0,
            'mentions': [],
            'found': False
        }
    
    async def _synthesize(self, company_name: str, hn_data: Dict) -> Dict:
        """Synthesize social media insights using LLM"""
        
        # Build prompt with available data
        prompt = f"""Analyze the social media presence for {company_name}.

Available data:
- HackerNews mentions: {hn_data.get('mentions_count', 0)}
- Sample discussions: {str(hn_data.get('mentions', []))[:1000]}

Based on this data (and your general knowledge), provide:
1. Overall sentiment (positive/neutral/negative)
2. Sentiment score (0-100)
3. Key themes being discussed
4. Positive feedback points
5. Negative feedback points
6. Trending topics

Return as JSON."""

        try:
            result = await self.llm.generate_structured(
                prompt=prompt,
                system_prompt="You are a social media analyst. Analyze sentiment and themes. If data is limited, use general knowledge about the company.",
                schema=SOCIAL_SENTIMENT_SCHEMA,
                task_type="fast"
            )
            return result
        except Exception as e:
            logger.error(f"❌ Social synthesis failed: {e}")
            return {
                "overall_sentiment": "neutral",
                "sentiment_score": 50,
                "key_themes": ["Unable to analyze"],
                "positive_feedback": [],
                "negative_feedback": [],
                "trending_topics": []
            }
