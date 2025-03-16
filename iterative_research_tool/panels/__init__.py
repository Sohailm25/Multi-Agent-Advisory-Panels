"""Multi-agent advisory panels package."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class BasePanel(ABC):
    """Base class for all advisory panels."""
    
    @abstractmethod
    def run(self, query: str, context: str) -> Dict[str, Any]:
        """Run the panel on the given query.
        
        Args:
            query: The query to run the panel on
            context: Context information
            
        Returns:
            The panel's output
        """
        pass 