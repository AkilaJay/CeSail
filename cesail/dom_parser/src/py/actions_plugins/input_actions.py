"""
Input actions plugin.
"""

from typing import Dict, Any
from playwright.async_api import Page
from .base_action import BaseAction
from ..types import Action, ActionType

class TypeAction(BaseAction):
    """Type text into an input field."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.TYPE
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Type text into an input field",
            "required_params": ["element_id", "text_to_type"],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            element = await self._get_element(action.element_id)
            if not element:
                return self._create_error_result(action, f"Element {action.element_id} not found or not visible")
            
            await element.fill(action.text_to_type)
            return self._create_success_result(action, text=action.text_to_type)
        except Exception as e:
            return self._create_error_result(action, str(e))

class CheckAction(BaseAction):
    """Check a checkbox or radio button."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.CHECK
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Check a checkbox or radio button",
            "required_params": ["element_id"],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            element = await self._get_element(action.element_id)
            if not element:
                return self._create_error_result(action, f"Element {action.element_id} not found or not visible")
            
            await element.check()
            return self._create_success_result(action)
        except Exception as e:
            return self._create_error_result(action, str(e))

class SelectAction(BaseAction):
    """Select an option from a dropdown."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.SELECT
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Select an option from a dropdown",
            "required_params": ["element_id", "options"],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            element = await self._get_element(action.element_id)
            if not element:
                return self._create_error_result(action, f"Element {action.element_id} not found or not visible")
            
            await element.select_option(value=action.options)
            return self._create_success_result(action, options=action.options)
        except Exception as e:
            return self._create_error_result(action, str(e))

class ClearAction(BaseAction):
    """Clear the content of an input field."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.CLEAR
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Clear the content of an input field",
            "required_params": ["element_id"],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            element = await self._get_element(action.element_id)
            if not element:
                return self._create_error_result(action, f"Element {action.element_id} not found or not visible")
            
            await element.clear()
            return self._create_success_result(action)
        except Exception as e:
            return self._create_error_result(action, str(e))

class PressKeyAction(BaseAction):
    """Press a keyboard key."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.PRESS_KEY
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Press a keyboard key",
            "required_params": [],
            "optional_params": ["metadata.key"]
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            metadata = action.metadata or {}
            key = metadata.get("key", "Enter")
            
            if action.element_id:
                element = await self._get_element(action.element_id)
                if element:
                    await element.press(key)
                else:
                    await self.page.keyboard.press(key)
            else:
                await self.page.keyboard.press(key)
            
            return self._create_success_result(action, key=key)
        except Exception as e:
            return self._create_error_result(action, str(e))

class KeyDownAction(BaseAction):
    """Press and hold a keyboard key."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.KEY_DOWN
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Press and hold a keyboard key",
            "required_params": [],
            "optional_params": ["metadata.key"]
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            metadata = action.metadata or {}
            key = metadata.get("key", "Shift")
            
            if action.element_id:
                element = await self._get_element(action.element_id)
                if element:
                    await element.press(key, delay=0)
                else:
                    await self.page.keyboard.down(key)
            else:
                await self.page.keyboard.down(key)
            
            return self._create_success_result(action, key=key)
        except Exception as e:
            return self._create_error_result(action, str(e))

class KeyUpAction(BaseAction):
    """Release a keyboard key."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.KEY_UP
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Release a keyboard key",
            "required_params": [],
            "optional_params": ["metadata.key"]
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            metadata = action.metadata or {}
            key = metadata.get("key", "Shift")
            
            await self.page.keyboard.up(key)
            return self._create_success_result(action, key=key)
        except Exception as e:
            return self._create_error_result(action, str(e))

class UploadFileAction(BaseAction):
    """Upload a file to a file input."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.UPLOAD_FILE
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Upload a file to a file input",
            "required_params": ["element_id"],
            "optional_params": ["metadata.file_path"]
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            element = await self._get_element(action.element_id)
            if not element:
                return self._create_error_result(action, f"Element {action.element_id} not found or not visible")
            
            metadata = action.metadata or {}
            file_path = metadata.get("file_path")
            if not file_path:
                return self._create_error_result(action, "File path is required for upload")
            
            await element.set_input_files(file_path)
            return self._create_success_result(action, file_path=file_path)
        except Exception as e:
            return self._create_error_result(action, str(e))

class SubmitAction(BaseAction):
    """Submit a form."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.SUBMIT
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Submit a form",
            "required_params": ["element_id"],
            "optional_params": []
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            element = await self._get_element(action.element_id)
            if not element:
                return self._create_error_result(action, f"Element {action.element_id} not found or not visible")
            
            await element.evaluate("el => el.form?.submit()")
            return self._create_success_result(action)
        except Exception as e:
            return self._create_error_result(action, str(e))

class DatePickAction(BaseAction):
    """Pick a date from a date input."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.DATE_PICK
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Pick a date from a date input",
            "required_params": ["element_id"],
            "optional_params": ["metadata.value"]
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            element = await self._get_element(action.element_id)
            if not element:
                return self._create_error_result(action, f"Element {action.element_id} not found or not visible")
            
            metadata = action.metadata or {}
            date_value = metadata.get("value", "2024-01-01")
            
            await element.fill(date_value)
            return self._create_success_result(action, value=date_value)
        except Exception as e:
            return self._create_error_result(action, str(e))

class SliderAction(BaseAction):
    """Set the value of a slider/range input."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.SLIDE
    
    @property
    def required_parameters(self) -> Dict[str, Any]:
        return {
            "description": "Set the value of a slider/range input",
            "required_params": ["element_id"],
            "optional_params": ["metadata.value"]
        }
    
    async def execute(self, action: Action) -> Dict[str, Any]:
        try:
            element = await self._get_element(action.element_id)
            if not element:
                return self._create_error_result(action, f"Element {action.element_id} not found or not visible")
            
            metadata = action.metadata or {}
            value = metadata.get("value", 50)
            
            await element.fill(str(value))
            return self._create_success_result(action, value=value)
        except Exception as e:
            return self._create_error_result(action, str(e)) 