from abc import ABC, abstractmethod
from typing import Dict, Any
from utils.logger import logger
from llm.groq_client import groq_client


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.llm = groq_client
        self.preferred_model = None  # ✅ NEW: Can be overridden
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent's main task"""
        pass
    
    async def _log_execution(self, context: Dict[str, Any]):
        """Log agent execution"""
        logger.info(f"[{self.name}] Executing with context keys: {list(context.keys())}")
    
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
    
    def _get_model_type(self, default: str) -> str:
        """Get model type - uses preference if set, otherwise default"""
        return self.preferred_model if self.preferred_model else default
