from abc import ABC, abstractmethod
from typing import Dict, Any
from utils.logger import logger


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
    
    @property
    def llm(self):
        """Get LLM client dynamically (not at import time)"""
        from llm.groq_client import groq_client
        return groq_client
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent's main task"""
        pass
    
    async def _log_execution(self, context: Dict[str, Any]):
        """Log agent execution"""
        logger.info(f"[{self.name}] Executing...")
    
    def _create_result(
        self,
        success: bool,
        data: Any,
        error: str = None,
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """Standard result format"""
        return {
            'agent': self.name,
            'success': success,
            'data': data,
            'error': error,
            'metadata': metadata or {}
        }
