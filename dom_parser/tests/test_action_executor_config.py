import pytest
from playwright.async_api import async_playwright
from dom_parser.src import DOMParser
from dom_parser.src.py.types import Action, ActionType

@pytest.mark.asyncio
async def test_action_executor_enabled_actions():
    """Test that ActionExecutor respects the enabled_actions configuration."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Test 1: All actions enabled (default behavior)
        config_all_enabled = {
            "action_executor": {
                "enabled_actions": [
                    "click", "type", "hover", "navigate", "back", "forward"
                ],
                "default_timeout_ms": 30000
            }
        }
        
        parser = DOMParser(config=config_all_enabled)
        async with parser:
            actions = parser.get_available_actions()
            available_action_names = list(actions["actions"].keys())
            
            # Should have the enabled actions
            assert "click" in available_action_names
            assert "type" in available_action_names
            assert "hover" in available_action_names
            assert "navigate" in available_action_names
            assert "back" in available_action_names
            assert "forward" in available_action_names
            
            # Should not have disabled actions
            assert "upload_file" not in available_action_names
            assert "close_tab" not in available_action_names
            assert "switch_tab" not in available_action_names
            
            # Test executing an enabled action
            click_action = Action(
                type=ActionType.CLICK,
                description="Test click",
                confidence=0.9,
                element_id="body",
                return_format={"element_id": str, "type": str}
            )
            result = await parser.action_executor.execute_action(click_action)
            assert result["success"] is True
            
            # Test executing a disabled action
            upload_action = Action(
                type=ActionType.UPLOAD_FILE,
                description="Test upload",
                confidence=0.9,
                element_id="input",
                return_format={"element_id": str, "type": str}
            )
            result = await parser.action_executor.execute_action(upload_action)
            assert result["success"] is False
            assert "not enabled" in result["error"]
        
        await browser.close()

@pytest.mark.asyncio
async def test_action_executor_minimal_config():
    """Test ActionExecutor with minimal enabled actions."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Test with only basic actions enabled
        minimal_config = {
            "action_executor": {
                "enabled_actions": ["click", "type"],
                "default_timeout_ms": 30000
            }
        }
        
        parser = DOMParser(config=minimal_config)
        async with parser:
            actions = parser.get_available_actions()
            available_action_names = list(actions["actions"].keys())
            
            # Should only have the minimal set
            assert len(available_action_names) == 2
            assert "click" in available_action_names
            assert "type" in available_action_names
            
            # Should not have other actions
            assert "hover" not in available_action_names
            assert "navigate" not in available_action_names
            assert "upload_file" not in available_action_names
        
        await browser.close()

@pytest.mark.asyncio
async def test_action_executor_no_enabled_actions():
    """Test ActionExecutor when no enabled_actions is specified (should enable all)."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Test with no enabled_actions specified - explicitly set to None to override default
        config_no_enabled = {
            "action_executor": {
                "enabled_actions": None,  # Explicitly set to None to override default
                "default_timeout_ms": 30000
            }
        }
        
        parser = DOMParser(config=config_no_enabled)
        async with parser:
            # Debug: Print the actual configuration being used
            print(f"Debug - Action executor config: {parser.config['action_executor']}")
            
            actions = parser.get_available_actions()
            available_action_names = list(actions["actions"].keys())
            
            print(f"Debug - Available actions: {available_action_names}")
            print(f"Debug - Number of actions: {len(available_action_names)}")
            
            # Should have many actions (all enabled by default)
            assert len(available_action_names) > 10
            
            # Should have common actions
            assert "click" in available_action_names
            assert "type" in available_action_names
            assert "hover" in available_action_names
            assert "navigate" in available_action_names
        
        await browser.close()

@pytest.mark.asyncio
async def test_action_executor_empty_enabled_actions():
    """Test ActionExecutor with empty enabled_actions list."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Test with empty enabled_actions list
        config_empty = {
            "action_executor": {
                "enabled_actions": [],
                "default_timeout_ms": 30000
            }
        }
        
        parser = DOMParser(config=config_empty)
        async with parser:
            actions = parser.get_available_actions()
            available_action_names = list(actions["actions"].keys())
            
            # Should have no actions when list is empty
            assert len(available_action_names) == 0
        
        await browser.close()

@pytest.mark.asyncio
async def test_action_executor_safety_config():
    """Test ActionExecutor with safety-focused configuration (disabling dangerous actions)."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Safety config - disable potentially dangerous actions
        safety_config = {
            "action_executor": {
                "enabled_actions": [
                    "click", "type", "hover", "select", "check", "clear", "submit",
                    "navigate", "back", "forward", "scroll_to", "scroll_by",
                    "right_click", "double_click", "focus", "blur",
                    "press_key", "key_down", "key_up",
                    "alert_accept", "alert_dismiss", "wait", "wait_for_selector", "wait_for_navigation"
                    # Note: upload_file, switch_tab, close_tab, switch_to_frame are disabled
                ],
                "default_timeout_ms": 30000
            }
        }
        
        parser = DOMParser(config=safety_config)
        async with parser:
            actions = parser.get_available_actions()
            available_action_names = list(actions["actions"].keys())
            
            # Should have safe actions
            assert "click" in available_action_names
            assert "type" in available_action_names
            assert "navigate" in available_action_names
            
            # Should not have dangerous actions
            assert "upload_file" not in available_action_names
            assert "close_tab" not in available_action_names
            assert "switch_tab" not in available_action_names
            assert "switch_to_frame" not in available_action_names
            
            # Test that disabled actions return appropriate error
            upload_action = Action(
                type=ActionType.UPLOAD_FILE,
                description="Test upload",
                confidence=0.9,
                element_id="input",
                return_format={"element_id": str, "type": str}
            )
            result = await parser.action_executor.execute_action(upload_action)
            assert result["success"] is False
            assert "not enabled" in result["error"]
        
        await browser.close()
