from agents.base_agent import BaseAgent
from scrapers.simple_scraper import scraper
from scrapers.extractors import extractor
from llm.prompts import WEB_RESEARCH_PROMPT, COMPANY_OVERVIEW_SCHEMA
from typing import Dict, Any, List
from utils.logger import logger


class WebResearchAgent(BaseAgent):
    """Agent for web research and data gathering"""
    
    def __init__(self):
        super().__init__("WebResearchAgent")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Research company via web scraping"""
        
        await self._log_execution(context)
        company_name = context.get('company_name')
        
        if not company_name:
            return self._create_result(False, None, "Missing company_name")
        
        try:
            # Step 1: Find company website
            logger.info(f"Finding website for {company_name}...")
            website_url = await scraper.find_company_website(company_name)
            
            if not website_url:
                # Return minimal data if website not found
                return self._create_result(
                    True,
                    {
                        "company_name": company_name,
                        "website_found": False,
                        "note": "Could not automatically find website. Using general knowledge."
                    },
                    metadata={'website': None}
                )
            
            # Step 2: Scrape key pages
            logger.info(f"Scraping pages from {website_url}...")
            pages_data = await self._scrape_company_pages(website_url)
            
            # Step 3: Extract structured data with LLM
            logger.info("Extracting structured information...")
            structured_data = await self._extract_structured_info(
                company_name,
                pages_data
            )
            
            return self._create_result(
                True,
                structured_data,
                metadata={'website': website_url, 'pages_scraped': len(pages_data)}
            )
            
        except Exception as e:
            logger.error(f"Web research failed: {e}")
            # Return partial success with error note
            return self._create_result(
                True,
                {
                    "company_name": company_name,
                    "error_note": f"Partial data due to: {str(e)}"
                },
                error=str(e)
            )
    
    async def _scrape_company_pages(self, base_url: str) -> List[Dict[str, Any]]:
        """Scrape important pages from company website"""
        
        # Common page patterns
        page_urls = [
            base_url,  # Homepage
            f"{base_url}/about",
            f"{base_url}/pricing",
            f"{base_url}/products",
        ]
        
        scraped_pages = []
        html_results = await scraper.scrape_multiple(page_urls[:3])  # Limit to 3 pages
        
        for url, html in html_results.items():
            if html:
                # Extract content
                main_content = extractor.extract_main_content(html, url)
                metadata = extractor.extract_metadata(html, url)
                
                if main_content:
                    scraped_pages.append({
                        'url': url,
                        'content': main_content[:3000],  # Limit content size
                        'metadata': metadata
                    })
                    logger.info(f"Extracted content from {url}")
        
        return scraped_pages
    
    async def _extract_structured_info(
        self,
        company_name: str,
        pages_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use LLM to extract structured information"""
        
        # Combine page contents
        if pages_data:
            combined_content = "\n\n".join([
                f"URL: {page['url']}\n{page['content'][:1500]}"
                for page in pages_data
            ])
        else:
            combined_content = "No web content available. Use general knowledge."
        
        prompt = WEB_RESEARCH_PROMPT.format(
            company_name=company_name,
            scraped_content=combined_content[:6000]  # Stay within token limits
        )
        
        try:
            structured_data = await self.llm.generate_structured(
                prompt=prompt,
                system_prompt="You are an expert at extracting company information. If data is not available, make reasonable inferences or state 'Unknown'.",
                schema=COMPANY_OVERVIEW_SCHEMA
            )
            return structured_data
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            # Return minimal valid structure
            return {
                "company_name": company_name,
                "tagline": "Unable to extract",
                "products": [],
                "target_market": "Unknown"
            }
