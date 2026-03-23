from agents.base_agent import BaseAgent
from scrapers.simple_scraper import scraper
from scrapers.extractors import extractor
from llm.prompts import WEB_RESEARCH_PROMPT, COMPANY_OVERVIEW_SCHEMA
from typing import Dict, Any, List
from utils.logger import logger


class WebResearchAgent(BaseAgent):
    """Web research agent"""
    
    def __init__(self):
        super().__init__("WebResearchAgent")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await self._log_execution(context)
        company_name = context.get('company_name')
        
        if not company_name:
            return self._create_result(False, None, "Missing company_name")
        
        try:
            logger.info(f"🔍 Finding website for {company_name}...")
            website_url = await scraper.find_company_website(company_name)
            
            if not website_url:
                return self._create_result(
                    True,
                    {"company_name": company_name, "website_found": False},
                    metadata={'website': None}
                )
            
            logger.info(f"📄 Scraping pages from {website_url}...")
            pages_data = await self._scrape_company_pages(website_url)
            
            logger.info("🧠 Extracting structured information...")
            structured_data = await self._extract_structured_info(company_name, pages_data)
            
            return self._create_result(
                True,
                structured_data,
                metadata={'website': website_url, 'pages_scraped': len(pages_data)}
            )
            
        except Exception as e:
            logger.error(f"❌ Web research failed: {e}")
            return self._create_result(
                True,
                {"company_name": company_name, "error_note": str(e)},
                error=str(e)
            )
    
    async def _scrape_company_pages(self, base_url: str) -> List[Dict]:
        page_urls = [base_url, f"{base_url}/about", f"{base_url}/pricing"]
        scraped = []
        html_results = await scraper.scrape_multiple(page_urls[:3])
        
        for url, html in html_results.items():
            if html:
                content = extractor.extract_main_content(html, url)
                if content:
                    scraped.append({'url': url, 'content': content[:3000]})
                    logger.info(f"✅ Extracted content from {url}")
        
        return scraped
    
    async def _extract_structured_info(self, company_name: str, pages_data: List[Dict]) -> Dict:
        if pages_data:
            combined = "\n\n".join([f"URL: {p['url']}\n{p['content'][:1500]}" for p in pages_data])
        else:
            combined = "No web content available."
        
        prompt = WEB_RESEARCH_PROMPT.format(
            company_name=company_name,
            scraped_content=combined[:6000]
        )
        
        try:
            return await self.llm.generate_structured(
                prompt=prompt,
                system_prompt="Extract company information accurately.",
                schema=COMPANY_OVERVIEW_SCHEMA,
                task_type="structured"
            )
        except Exception as e:
            logger.error(f"❌ LLM extraction failed: {e}")
            return {"company_name": company_name, "products": []}
