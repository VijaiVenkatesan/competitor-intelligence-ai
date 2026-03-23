from bs4 import BeautifulSoup
from trafilatura import extract
from typing import Dict, Optional
from utils.logger import logger


class ContentExtractor:
    """Extract structured data from HTML"""
    
    @staticmethod
    def extract_main_content(html: str, url: str) -> Optional[str]:
        """Extract main text content using trafilatura"""
        
        try:
            content = extract(
                html,
                include_comments=False,
                include_tables=True,
                no_fallback=False
            )
            
            if content:
                return content
            
            # Fallback to BeautifulSoup
            return ContentExtractor._fallback_extraction(html)
            
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return ContentExtractor._fallback_extraction(html)
    
    @staticmethod
    def _fallback_extraction(html: str) -> str:
        """Fallback extraction using BeautifulSoup"""
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            return '\n'.join(lines)
            
        except Exception as e:
            logger.error(f"Fallback extraction failed: {e}")
            return ""
    
    @staticmethod
    def extract_metadata(html: str, url: str) -> Dict[str, str]:
        """Extract page metadata"""
        
        soup = BeautifulSoup(html, 'html.parser')
        
        metadata = {
            'url': url,
            'title': '',
            'description': '',
            'keywords': ''
        }
        
        # Title
        if soup.title:
            metadata['title'] = soup.title.string.strip() if soup.title.string else ''
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                metadata['description'] = content
            elif name == 'keywords':
                metadata['keywords'] = content
        
        return metadata


# Global instance
extractor = ContentExtractor()
