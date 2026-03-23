import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import asyncio
from typing import Optional
from utils.logger import logger


class SimpleScraper:
    """
    Simplified scraper for Streamlit Cloud
    No Playwright/Selenium (not supported on Streamlit Cloud)
    """
    
    def __init__(self):
        self.ua = UserAgent()
        self.timeout = 15
    
    async def scrape_url(self, url: str) -> Optional[str]:
        """Scrape URL and return HTML"""
        
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    return response.text
                else:
                    logger.warning(f"Failed to scrape {url}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    async def scrape_multiple(self, urls: list) -> dict:
        """Scrape multiple URLs"""
        
        results = {}
        
        for url in urls:
            html = await self.scrape_url(url)
            if html:
                results[url] = html
            
            # Rate limiting
            await asyncio.sleep(2)
        
        return results
