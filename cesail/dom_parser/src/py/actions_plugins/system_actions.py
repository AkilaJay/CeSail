"""
System actions plugin.
"""

from typing import Dict, Any
from playwright.async_api import Page
from .base_action import BaseAction
from ..types import Action, ActionType

class AlertAcceptAction(BaseAction):
    """Accept a JavaScript alert."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.ALERT_ACCEPT
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Accept a JavaScript alert",
            "required_params": [],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            # Wait for dialog and accept it
            dialog = await self.page.wait_for_event('dialog')
            await dialog.accept()
            return self._create_success_result(action)
        except Exception as e:
            return self._create_error_result(action, str(e))

class AlertDismissAction(BaseAction):
    """Dismiss a JavaScript alert."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.ALERT_DISMISS
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Dismiss a JavaScript alert",
            "required_params": [],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            # Wait for dialog and dismiss it
            dialog = await self.page.wait_for_event('dialog')
            await dialog.dismiss()
            return self._create_success_result(action)
        except Exception as e:
            return self._create_error_result(action, str(e))

class WaitAction(BaseAction):
    """Wait for a specified duration."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.WAIT
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Wait for a specified duration",
            "required_params": [],
            "optional_params": ["metadata.timeout"]
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            metadata = action.metadata or {}
            timeout = metadata.get("timeout", 1000)  # Default 1 second
            
            await self.page.wait_for_timeout(timeout)
            return self._create_success_result(action, timeout=timeout)
        except Exception as e:
            return self._create_error_result(action, str(e))

class WaitForSelectorAction(BaseAction):
    """Wait for an element to appear."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.WAIT_FOR_SELECTOR
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Wait for an element to appear",
            "required_params": [],
            "optional_params": ["metadata.selector", "metadata.state", "metadata.timeout"]
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            metadata = action.metadata or {}
            selector = metadata.get("selector")
            state = metadata.get("state", "visible")
            timeout = metadata.get("timeout", 30000)  # Default 30 seconds
            
            if not selector:
                return self._create_error_result(action, "Selector is required for wait_for_selector")
            
            if state == "visible":
                await self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            elif state == "hidden":
                await self.page.wait_for_selector(selector, state="hidden", timeout=timeout)
            else:
                await self.page.wait_for_selector(selector, timeout=timeout)
            
            return self._create_success_result(action, selector=selector, state=state, timeout=timeout)
        except Exception as e:
            return self._create_error_result(action, str(e))

class WaitForNavigationAction(BaseAction):
    """Wait for page navigation to complete."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.WAIT_FOR_NAVIGATION
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Wait for page navigation to complete",
            "required_params": [],
            "optional_params": ["metadata.timeout"]
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            metadata = action.metadata or {}
            timeout = metadata.get("timeout", 30000)  # Default 30 seconds
            
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
            return self._create_success_result(action, timeout=timeout)
        except Exception as e:
            return self._create_error_result(action, str(e)) 