"""
Base action class for all action plugins.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from playwright.async_api import Page, ElementHandle
from ..types import Action, ActionType


class BaseAction(ABC):
    """Base class for all action plugins."""
    
    def __init__(self, page: Page):
        self.page = page
    
    @property
    @abstractmethod
    def action_type(self) -> ActionType:
        """The action type this plugin handles."""
        pass
    
    @abstractmethod
    async def execute(self, action: Action) -> Dict[str, Any]:
        """Execute the action and return the result."""
        pass
    
    async def _get_element(self, element_id: str) -> Optional[ElementHandle]:
        """Get an element by its ID and ensure it's visible."""
        element = await self.page.query_selector(element_id)
        if element and await element.is_visible():
            return element
        return None
    
    def _create_success_result(self, action: Action, **kwargs) -> Dict[str, Any]:
        """Create a success result dictionary."""
        result = {
            "success": True,
            "type": action.type.value,
            "element_id": action.element_id,
            "action": action.dict()
        }
        result.update(kwargs)
        return result
    
    def _create_error_result(self, action: Action, error: str) -> Dict[str, Any]:
        """Create an error result dictionary."""
        return {
            "success": False,
            "error": error,
            "action": action.dict()
        } 