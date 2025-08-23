"""
Interaction actions plugin.
"""

from typing import Dict, Any
from playwright.async_api import Page
from .base_action import BaseAction
from ..types import Action, ActionType

class ClickAction(BaseAction):
    """Click on an element."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.CLICK
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Click on an element",
            "required_params": ["element_id"],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            element = await self._get_element(action.element_id)
            if not element:
                return self._create_error_result(action, f"Element {action.element_id} not found or not visible")
            
            await element.click()
            return self._create_success_result(action)
        except Exception as e:
            return self._create_error_result(action, str(e))

class RightClickAction(BaseAction):
    """Right-click on an element."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.RIGHT_CLICK
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Right-click on an element",
            "required_params": ["element_id"],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            element = await self._get_element(action.element_id)
            if not element:
                return self._create_error_result(action, f"Element {action.element_id} not found or not visible")
            
            await element.click(button="right")
            return self._create_success_result(action)
        except Exception as e:
            return self._create_error_result(action, str(e))

class DoubleClickAction(BaseAction):
    """Double-click on an element."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.DOUBLE_CLICK
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Double-click on an element",
            "required_params": ["element_id"],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            element = await self._get_element(action.element_id)
            if not element:
                return self._create_error_result(action, f"Element {action.element_id} not found or not visible")
            
            await element.dblclick()
            return self._create_success_result(action)
        except Exception as e:
            return self._create_error_result(action, str(e))

class HoverAction(BaseAction):
    """Hover over an element."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.HOVER
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Hover over an element",
            "required_params": ["element_id"],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            element = await self._get_element(action.element_id)
            if not element:
                return self._create_error_result(action, f"Element {action.element_id} not found or not visible")
            
            await element.hover()
            return self._create_success_result(action)
        except Exception as e:
            return self._create_error_result(action, str(e))

class FocusAction(BaseAction):
    """Focus on an element."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.FOCUS
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Focus on an element",
            "required_params": ["element_id"],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            element = await self._get_element(action.element_id)
            if not element:
                return self._create_error_result(action, f"Element {action.element_id} not found or not visible")
            
            await element.focus()
            return self._create_success_result(action)
        except Exception as e:
            return self._create_error_result(action, str(e))

class BlurAction(BaseAction):
    """Remove focus from an element."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.BLUR
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Remove focus from an element",
            "required_params": ["element_id"],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            element = await self._get_element(action.element_id)
            if not element:
                return self._create_error_result(action, f"Element {action.element_id} not found or not visible")
            
            await element.evaluate("el => el.blur()")
            return self._create_success_result(action)
        except Exception as e:
            return self._create_error_result(action, str(e))

class ScrollToAction(BaseAction):
    """Scroll to a specific element."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.SCROLL_TO
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Scroll to a specific element",
            "required_params": ["element_id"],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            element = await self.page.query_selector(action.element_id)
            if not element:
                return self._create_error_result(action, f"Element {action.element_id} not found")
            
            await element.scroll_into_view_if_needed()
            return self._create_success_result(action)
        except Exception as e:
            return self._create_error_result(action, str(e))

class ScrollByAction(BaseAction):
    """Scroll by a specific amount."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.SCROLL_BY
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Scroll by a specific amount",
            "required_params": ["metadata.x", "metadata.y"],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            metadata = action.metadata or {}
            x = metadata.get("x", 0)
            y = metadata.get("y", 0)
            
            await self.page.evaluate(f"window.scrollBy({x}, {y})")
            return self._create_success_result(action, x=x, y=y)
        except Exception as e:
            return self._create_error_result(action, str(e))

class ScrollDownViewportAction(BaseAction):
    """Scroll down one viewport height."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.SCROLL_DOWN_VIEWPORT
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Scroll down one viewport height",
            "required_params": [],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            viewport_height = await self.page.evaluate("window.innerHeight")
            await self.page.evaluate(f"window.scrollBy(0, {viewport_height})")
            return self._create_success_result(action)
        except Exception as e:
            return self._create_error_result(action, str(e))

class DragDropAction(BaseAction):
    """Drag and drop an element."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.DRAG_DROP
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Drag and drop an element",
            "required_params": ["element_id"],
            "optional_params": ["metadata.target_id"]
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            source_element = await self._get_element(action.element_id)
            if not source_element:
                return self._create_error_result(action, f"Source element {action.element_id} not found or not visible")
            
            metadata = action.metadata or {}
            target_id = metadata.get("target_id")
            if target_id:
                target_element = await self._get_element(target_id)
                if not target_element:
                    return self._create_error_result(action, f"Target element {target_id} not found or not visible")
                
                await source_element.drag_to(target_element)
            else:
                # Drag to a random position
                await source_element.drag_to(source_element)
            
            return self._create_success_result(action, target_id=target_id)
        except Exception as e:
            return self._create_error_result(action, str(e)) 