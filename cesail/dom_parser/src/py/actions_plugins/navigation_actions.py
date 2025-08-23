"""
Navigation actions plugin.
"""

from typing import Dict, Any
from playwright.async_api import Page
from .base_action import BaseAction
from ..types import Action, ActionType

class NavigateAction(BaseAction):
    """Navigate to a URL."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.NAVIGATE
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Navigate to a URL",
            "required_params": ["metadata.url"],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            url = action.metadata.get("url") if action.metadata else None
            if not url:
                return self._create_error_result(action, "URL is required for navigation")
            
            await self.page.goto(url)
            return self._create_success_result(action, url=url)
        except Exception as e:
            return self._create_error_result(action, str(e))

class BackAction(BaseAction):
    """Navigate back in browser history."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.BACK
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Navigate back in browser history",
            "required_params": [],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            await self.page.go_back()
            return self._create_success_result(action)
        except Exception as e:
            return self._create_error_result(action, str(e))

class ForwardAction(BaseAction):
    """Navigate forward in browser history."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.FORWARD
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Navigate forward in browser history",
            "required_params": [],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            await self.page.go_forward()
            return self._create_success_result(action)
        except Exception as e:
            return self._create_error_result(action, str(e))

class SwitchTabAction(BaseAction):
    """Switch to a different browser tab."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.SWITCH_TAB
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Switch to a different browser tab",
            "required_params": [],
            "optional_params": ["metadata.tab_index"]
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            tab_index = action.metadata.get("tab_index", 0) if action.metadata else 0
            context = self.page.context
            pages = context.pages
            if tab_index < len(pages):
                self.page = pages[tab_index]
                return self._create_success_result(action, tab_index=tab_index)
            else:
                return self._create_error_result(action, f"Tab index {tab_index} not found")
        except Exception as e:
            return self._create_error_result(action, str(e))

class CloseTabAction(BaseAction):
    """Close the current browser tab."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.CLOSE_TAB
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Close the current browser tab",
            "required_params": [],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            context = self.page.context
            pages = context.pages
            if len(pages) > 1:
                await self.page.close()
                # Switch to the first remaining page
                self.page = context.pages[0]
                return self._create_success_result(action)
            else:
                return self._create_error_result(action, "Cannot close the last tab")
        except Exception as e:
            return self._create_error_result(action, str(e))

class SwitchToFrameAction(BaseAction):
    """Switch to an iframe."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.SWITCH_TO_FRAME
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Switch to an iframe",
            "required_params": [],
            "optional_params": ["metadata.frame_name"]
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            frame_name = action.metadata.get("frame_name") if action.metadata else None
            if frame_name:
                frame = self.page.frame_locator(f'iframe[name="{frame_name}"]')
                self.page = frame.page
            else:
                # Switch to the first iframe
                frames = self.page.frames
                if len(frames) > 1:
                    self.page = frames[1]  # First frame is main page
                else:
                    return self._create_error_result(action, "No iframes found")
            return self._create_success_result(action, frame_name=frame_name)
        except Exception as e:
            return self._create_error_result(action, str(e))

class SwitchToParentFrameAction(BaseAction):
    """Switch back to the parent frame."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.SWITCH_TO_PARENT_FRAME
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Switch back to the parent frame",
            "required_params": [],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            # Switch back to the main page
            context = self.page.context
            self.page = context.pages[0]
            return self._create_success_result(action)
        except Exception as e:
            return self._create_error_result(action, str(e)) 