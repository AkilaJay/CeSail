"""
Simple test for the MCP server functionality without requiring MCP client library.
"""

import pytest
import asyncio
import json
import subprocess
import sys
from pathlib import Path


@pytest.mark.asyncio
async def test_mcp_server_basic_functionality():
    """Test basic MCP server functionality by running it directly."""
    
    # Test that the server can be imported and initialized
    try:
        # Add the dom_parser directory to Python path
        dom_parser_path = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(dom_parser_path))
        
        # Import the server
        from cesail_mcp.fastmcp_server import fastmcp_server
        
        # Test server initialization
        server = DOMParserMCPServer()
        assert server is not None
        assert hasattr(server, 'dom_parser')
        assert hasattr(server, 'server')
        
        print("✓ MCP Server imports and initializes successfully")
        
    except ImportError as e:
        pytest.skip(f"MCP server dependencies not available: {e}")
    except Exception as e:
        pytest.fail(f"Failed to initialize MCP server: {e}")


@pytest.mark.asyncio
async def test_dom_parser_integration():
    """Test the underlying DOMParser functionality that the MCP server uses."""
    
    try:
        from dom_parser.src import DOMParser, Action, ActionType
        
        async with DOMParser(headless=True) as parser:
            # Test navigation
            navigate_action = Action(
                type=ActionType.NAVIGATE,
                description="Navigate to example.com",
                confidence=1.0,
                metadata={"url": "https://example.com"}
            )
            
            result = await parser.execute_action(navigate_action, wait_for_idle=True)
            assert result.get('success', False), f"Navigation failed: {result.get('error', 'Unknown error')}"
            print("✓ Navigation to example.com successful")
            
            # Test page analysis
            parsed_page = await parser.analyze_page()
            assert parsed_page is not None
            assert hasattr(parsed_page, 'metadata')
            assert hasattr(parsed_page, 'actions')
            print(f"✓ Page analysis successful - {len(parsed_page.actions.actions)} actions found")
            
            # Test available actions
            available_actions = parser.get_available_actions()
            assert available_actions is not None
            assert len(available_actions) > 0
            print(f"✓ Available actions retrieved - {len(available_actions)} action types")
            
    except ImportError as e:
        pytest.skip(f"DOMParser dependencies not available: {e}")
    except Exception as e:
        pytest.fail(f"DOMParser integration test failed: {e}")


@pytest.mark.asyncio
async def test_action_execution():
    """Test action execution functionality."""
    
    try:
        from dom_parser.src import DOMParser, Action, ActionType
        
        async with DOMParser(headless=True) as parser:
            # Navigate first
            navigate_action = Action(
                type=ActionType.NAVIGATE,
                description="Navigate to example.com",
                confidence=1.0,
                metadata={"url": "https://example.com"}
            )
            await parser.execute_action(navigate_action, wait_for_idle=True)
            
            # Test different action types
            action_tests = [
                {
                    "name": "Wait Action",
                    "action": Action(
                        type=ActionType.WAIT,
                        metadata={"duration_ms": 1000},
                        description="Wait for 1 second",
                        confidence=1.0
                    )
                },
                {
                    "name": "Scroll Action", 
                    "action": Action(
                        type=ActionType.SCROLL_DOWN_VIEWPORT,
                        description="Scroll down viewport",
                        confidence=1.0
                    )
                }
            ]
            
            for test in action_tests:
                result = await parser.execute_action(test["action"], wait_for_idle=True)
                assert result.get('success', False), f"{test['name']} failed: {result.get('error', 'Unknown error')}"
                print(f"✓ {test['name']} successful")
                
    except ImportError as e:
        pytest.skip(f"DOMParser dependencies not available: {e}")
    except Exception as e:
        pytest.fail(f"Action execution test failed: {e}")


@pytest.mark.asyncio
async def test_page_analysis_output():
    """Test that page analysis produces the expected output format."""
    
    try:
        from dom_parser.src import DOMParser, Action, ActionType
        
        async with DOMParser(headless=True) as parser:
            # Navigate to a page
            navigate_action = Action(
                type=ActionType.NAVIGATE,
                description="Navigate to example.com",
                confidence=1.0,
                metadata={"url": "https://example.com"}
            )
            await parser.execute_action(navigate_action, wait_for_idle=True)
            
            # Analyze page
            parsed_page = await parser.analyze_page()
            
            # Test the structure matches what MCP server expects
            assert hasattr(parsed_page, 'metadata')
            assert hasattr(parsed_page.metadata, 'url')
            assert hasattr(parsed_page.metadata, 'title')
            
            assert hasattr(parsed_page, 'actions')
            assert hasattr(parsed_page.actions, 'actions')
            
            assert hasattr(parsed_page, 'important_elements')
            assert hasattr(parsed_page.important_elements, 'elements')
            
            # Test that actions have the expected fields
            if parsed_page.actions.actions:
                action = parsed_page.actions.actions[0]
                assert hasattr(action, 'type')
                assert hasattr(action, 'description')
                assert hasattr(action, 'element_id')
                assert hasattr(action, 'confidence')
                
                print(f"✓ Action structure valid - {action.type.value}: {action.description}")
            
            print(f"✓ Page analysis structure valid - {len(parsed_page.actions.actions)} actions, {len(parsed_page.important_elements.elements)} elements")
            
    except ImportError as e:
        pytest.skip(f"DOMParser dependencies not available: {e}")
    except Exception as e:
        pytest.fail(f"Page analysis output test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_mcp_server_basic_functionality())
    asyncio.run(test_dom_parser_integration())
    asyncio.run(test_action_execution())
    asyncio.run(test_page_analysis_output()) 