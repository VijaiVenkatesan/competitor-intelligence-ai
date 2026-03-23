import httpx
from fake_useragent import UserAgent
import asyncio
from typing import Optional, List
from utils.logger import logger


class SimpleScraper:
    """
    Simplified HTTP-based scraper for Streamlit Cloud
    No Playwright/Selenium needed
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
            'Connection': 'keep-alive',
        }
        
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                verify=False
            ) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    logger.info(f"Successfully scraped: {url}")
                    return response.text
                else:
                    logger.warning(f"Failed to scrape {url}: HTTP {response.status_code}")
                    return None
                    
        except httpx.TimeoutException:
            logger.warning(f"Timeout scraping {url}")
            return None
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    async def scrape_multiple(self, urls: List[str]) -> dict:
        """Scrape multiple URLs with rate limiting"""
        
        results = {}
        
        for i, url in enumerate(urls):
            logger.info(f"Scraping {i+1}/{len(urls)}: {url}")
            
            html = await self.scrape_url(url)
            if html:
                results[url] = html
            
            # Rate limiting - be nice to servers
            if i < len(urls) - 1:
                await asyncio.sleep(2)
        
        return results
    
    async def find_company_website(self, company_name: str) -> Optional[str]:
        """Attempt to find company website"""
        
        # Try common domain patterns
        domain_variants = [
            f"https://www.{company_name.lower().replace(' ', '')}.com",
            f"https://{company_name.lower().replace(' ', '')}.com",
            f"https://www.{company_name.lower().replace(' ', '')}.io",
            f"https://{company_name.lower().replace(' ', '')}.io",
            f"https://www.{company_name.lower().replace(' ', '')}.ai",
            f"https://www.{company_name.lower().replace(' ', 'dash')}.com",
        ]
        
        for url in domain_variants:
            html = await self.scrape_url(url)
            if html and len(html) > 1000:  # Valid page
                logger.info(f"Found website: {url}")
                return url
        
        return None


# Global instance
scraper = SimpleScraper()
