from typing import Dict, List, Optional, Any, Type
from playwright.async_api import Page, ElementHandle
from .types import Action, ActionType, DOMDiff, SideEffect
from .actions_plugins import BaseAction
from .actions_plugins.navigation_actions import (
    NavigateAction, BackAction, ForwardAction, SwitchTabAction,
    CloseTabAction, SwitchToFrameAction, SwitchToParentFrameAction
)
from .actions_plugins.interaction_actions import (
    ClickAction, RightClickAction, DoubleClickAction, HoverAction,
    FocusAction, BlurAction, ScrollToAction, ScrollByAction,
    ScrollDownViewportAction, DragDropAction
)
from .actions_plugins.input_actions import (
    TypeAction, CheckAction, SelectAction, ClearAction, PressKeyAction,
    KeyDownAction, KeyUpAction, UploadFileAction, SubmitAction,
    DatePickAction, SliderAction
)
from .actions_plugins.system_actions import (
    AlertAcceptAction, AlertDismissAction, WaitAction,
    WaitForSelectorAction, WaitForNavigationAction
)


class ActionExecutor:
    def __init__(self, page: Page, **config):
        self.page = page
        self.config = config
        self._action_plugins: Dict[ActionType, Type[BaseAction]] = {}
        self._initialize_action_plugins()
    
    def _initialize_action_plugins(self):
        """Initialize the action plugins map with error checking for duplicates."""
        all_plugins = [
            # Navigation actions
            NavigateAction, BackAction, ForwardAction, SwitchTabAction,
            CloseTabAction, SwitchToFrameAction, SwitchToParentFrameAction,

            # Interaction actions
            ClickAction, RightClickAction, DoubleClickAction, HoverAction,
            FocusAction, BlurAction, ScrollToAction, ScrollByAction,
            ScrollDownViewportAction, DragDropAction,

            # Input actions
            TypeAction, CheckAction, SelectAction, ClearAction, PressKeyAction,
            KeyDownAction, KeyUpAction, UploadFileAction, SubmitAction,
            DatePickAction, SliderAction,

            # System actions
            AlertAcceptAction, AlertDismissAction, WaitAction,
            WaitForSelectorAction, WaitForNavigationAction
        ]

        # Get enabled actions from config
        enabled_actions = self.config.get("enabled_actions", None)
        
        for plugin_class in all_plugins:
            temp_instance = plugin_class(self.page)
            action_type = temp_instance.action_type
            action_name = action_type.value
            
            # If enabled_actions is None (not specified), enable all actions
            # If enabled_actions is an empty list, disable all actions
            # If enabled_actions is a list, only include actions in the list
            if enabled_actions is None:
                # Enable all actions when not specified
                pass
            elif len(enabled_actions) == 0:
                # Disable all actions when empty list
                continue
            elif action_name not in enabled_actions:
                # Only include actions that are explicitly enabled
                continue
                
            if action_type in self._action_plugins:
                existing_plugin = self._action_plugins[action_type].__name__
                raise ValueError(f"Duplicate action type {action_type} found: {plugin_class.__name__} conflicts with {existing_plugin}")
            self._action_plugins[action_type] = plugin_class
    
    def _get_action_plugin(self, action_type: ActionType) -> Optional[Type[BaseAction]]:
        """Get the plugin class for a given action type."""
        return self._action_plugins.get(action_type)
    
    def get_available_actions(self) -> Dict[str, Any]:
        """Get comprehensive information about all available action plugins."""
        actions = {}
        for action_type, plugin_class in self._action_plugins.items():
            temp_instance = plugin_class(self.page)
            actions[action_type.value] = temp_instance.required_parameters

        return {
            "actions": actions,
            "common_parameters": {
                "element_id": {
                    "type": "string",
                    "description": "CSS selector or unique identifier for the target element"
                },
                "text_to_type": {
                    "type": "string", 
                    "description": "Text to be typed into an input field"
                },
                "options": {
                    "type": "string",
                    "description": "Value of the option to select"
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional parameters specific to each action type",
                    "properties": {
                        "key": "string for keyboard actions",
                        "file_path": "string for file uploads", 
                        "target_id": "string for drag and drop",
                        "selector": "string for wait_for_selector",
                        "state": "string for wait_for_selector",
                        "timeout": "number for various wait actions",
                        "frame_name": "string for frame switching",
                        "tab_index": "number for tab switching",
                        "x": "number for scroll_by",
                        "y": "number for scroll_by",
                        "value": "string/number for date_pick, slider, etc.",
                        "url": "string for navigation"
                    }
                }
            }
        }

    async def execute_action(self, action: Action) -> Dict[str, Any]:
        """Execute an action using the appropriate plugin."""
        try:
            if action.element_id is None and action.type not in [ActionType.BACK, ActionType.FORWARD, ActionType.NAVIGATE]:
                action.element_id = "body"
            
            plugin_class = self._get_action_plugin(action.type)
            if plugin_class is None:
                return {
                    "success": False,
                    "error": f"Action type '{action.type.value}' is not enabled or not supported",
                    "action": action.model_dump()
                }
            
            plugin_instance = plugin_class(self.page)
            return await plugin_instance.execute(action)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": action.model_dump()
            }

    async def execute_actions(self, actions: list[Action]) -> list[Dict[str, Any]]:
        """Execute multiple actions in sequence."""
        results = []
        for action in actions:
            result = await self.execute_action(action)
            results.append(result)
        return results

    async def execute_action_from_json(self, action_json: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action from JSON input."""
        action = Action(**action_json)
        return await self.execute_action(action)
