"""
Comprehensive tests for the DOM Parser MCP Server.
"""

import asyncio
import json
import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


async def test_mcp_server_comprehensive():
    """Test the MCP server with a comprehensive workflow."""
    
    # Set up server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["dom_parser/cesail_mcp/fastmcp_server.py"]
    )
    
    print("=== Starting Comprehensive MCP Server Test ===")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            print("Initializing session...")
            result = await session.initialize()
            print(f"Initialize result: {result}")
            
            # List available tools
            print("\nListing tools...")
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")
            print()
            
            # Test 1: Navigate to a simple test page
            print("=== Test 1: Navigate to Test Page ===")
            navigate_action = {
                "type": "navigate",
                "description": "Navigate to a test page",
                "element_id": None,
                "confidence": 1.0,
                "text_to_type": None,
                "value": None,
                "metadata": {"url": "https://example.com"}
            }
            
            result = await session.call_tool(
                "execute_action",
                {"ui_action": navigate_action}
            )
            print("Navigation result:")
            for content in result.content:
                if hasattr(content, 'text'):
                    try:
                        # Try to parse as JSON for better formatting
                        data = json.loads(content.text)
                        print(json.dumps(data, indent=2))
                    except json.JSONDecodeError:
                        # If it's not valid JSON, print as regular text
                        print(content.text)
            print()
            
            # Test 2: Get page details
            print("=== Test 2: Get Page Details ===")
            result = await session.call_tool(
                "get_page_details",
                {"headless": False}
            )
            print("Page details result:")
            for content in result.content:
                if hasattr(content, 'text'):
                    try:
                        # Try to parse as JSON for better formatting
                        data = json.loads(content.text)
                        print(json.dumps(data, indent=2))
                    except json.JSONDecodeError:
                        # If it's not valid JSON, print as regular text
                        print(content.text)
            print()
            
            # Test 3: Execute a click action (if we have actions)
            print("=== Test 3: Execute Click Action ===")
            # This would typically use an action from the page details
            # For now, we'll test with a dummy action
            click_action = {
                "type": "click",
                "description": "Click on a link",
                "element_id": "test-element",
                "confidence": 0.8,
                "text_to_type": None,
                "value": None,
                "metadata": {}
            }
            
            result = await session.call_tool(
                "execute_action",
                {"ui_action": click_action}
            )
            print("Click action result:")
            for content in result.content:
                if hasattr(content, 'text'):
                    try:
                        # Try to parse as JSON for better formatting
                        data = json.loads(content.text)
                        print(json.dumps(data, indent=2))
                    except json.JSONDecodeError:
                        # If it's not valid JSON, print as regular text
                        print(content.text)
            print()
            
            # Test 4: Error handling - invalid action type
            print("=== Test 4: Error Handling ===")
            invalid_action = {
                "type": "invalid_action_type",
                "description": "This should fail",
                "element_id": None,
                "confidence": 1.0,
                "text_to_type": None,
                "value": None,
                "metadata": {}
            }
            
            result = await session.call_tool(
                "execute_action",
                {"ui_action": invalid_action}
            )
            print("Invalid action result:")
            for content in result.content:
                if hasattr(content, 'text'):
                    try:
                        # Try to parse as JSON for better formatting
                        data = json.loads(content.text)
                        print(json.dumps(data, indent=2))
                    except json.JSONDecodeError:
                        # If it's not valid JSON, print as regular text
                        print(content.text)
            print()
            
            # Test 5: Test unknown tool
            print("=== Test 5: Unknown Tool ===")
            try:
                result = await session.call_tool(
                    "unknown_tool",
                    {}
                )
                print("Unknown tool result:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        try:
                            # Try to parse as JSON for better formatting
                            data = json.loads(content.text)
                            print(json.dumps(data, indent=2))
                        except json.JSONDecodeError:
                            # If it's not valid JSON, print as regular text
                            print(content.text)
            except Exception as e:
                print(f"Expected error for unknown tool: {e}")
            print()
            
            print("=== Test Complete ===")


# async def test_mcp_server_google_flights_workflow():
#     """Test a realistic Google Flights workflow using the MCP server."""
    
#     server_params = StdioServerParameters(
#         command="python",
#         args=["dom_parser/cesail_mcp/fastmcp_server.py"]
#     )
    
#     print("=== Starting Google Flights Workflow Test ===")
    
#     async with stdio_client(server_params) as (read, write):
#         async with ClientSession(read, write) as session:
#             await session.initialize()
            
#             # Step 1: Navigate to Google Flights
#             print("Step 1: Navigating to Google Flights...")
#             navigate_action = {
#                 "type": "navigate",
#                 "description": "Navigate to Google Flights",
#                 "element_id": None,
#                 "confidence": 1.0,
#                 "text_to_type": None,
#                 "value": None,
#                 "metadata": {"url": "https://www.google.com/travel/flights"}
#             }
            
#             result = await session.call_tool(
#                 "execute_action",
#                 {"ui_action": navigate_action}
#             )
#             print("Navigation result:")
#             for content in result.content:
#                 if hasattr(content, 'text'):
#                     print(content.text)
#             print()
            
#             # Step 2: Get page details to understand the page
#             print("Step 2: Getting page details...")
#             result = await session.call_tool(
#                 "get_page_details",
#                 {"headless": False}
#             )
            
#             page_data = None
#             for content in result.content:
#                 if hasattr(content, 'text'):
#                     try:
#                         page_data = json.loads(content.text)
#                         print("Page analysis complete!")
#                         print(f"Found {page_data.get('actions_count', 0)} actions")
#                         print(f"Found {page_data.get('elements_count', 0)} elements")
#                         break
#                     except:
#                         print(content.text)
            
#             # Step 3: Try to find and click on a search box
#             if page_data and page_data.get('parsed_actions'):
#                 print("Step 3: Looking for search actions...")
#                 search_actions = [
#                     action for action in page_data['parsed_actions']
#                     if 'search' in action.get('description', '').lower() or
#                        'input' in action.get('description', '').lower() or
#                        'type' in action.get('type', '').lower()
#                 ]
                
#                 if search_actions:
#                     print(f"Found {len(search_actions)} potential search actions")
#                     # Use the first search action
#                     search_action = search_actions[0]
#                     print(f"Using action: {search_action['description']}")
                    
#                     # Create a type action
#                     type_action = {
#                         "type": "type",
#                         "description": f"Type into {search_action['description']}",
#                         "element_id": search_action['element_id'],
#                         "confidence": 0.9,
#                         "text_to_type": "New York to London",
#                         "value": None,
#                         "metadata": {}
#                     }
                    
#                     result = await session.call_tool(
#                         "execute_action",
#                         {"ui_action": type_action}
#                     )
#                     print("Type action result:")
#                     for content in result.content:
#                         if hasattr(content, 'text'):
#                             print(content.text)
#                 else:
#                     print("No search actions found")
            
#             print("=== Google Flights Workflow Test Complete ===")


# async def test_mcp_server_error_handling():
#     """Test error handling in the MCP server."""
    
#     server_params = StdioServerParameters(
#         command="python",
#         args=["dom_parser/cesail_mcp/fastmcp_server.py"]
#     )
    
#     print("=== Starting Error Handling Test ===")
    
#     async with stdio_client(server_params) as (read, write):
#         async with ClientSession(read, write) as session:
#             await session.initialize()
            
#             # Test 1: Invalid action without required parameters
#             print("Test 1: Invalid action without required parameters")
#             invalid_action = {
#                 "type": "navigate",
#                 "description": "Navigate without URL",
#                 "element_id": None,
#                 "confidence": 1.0,
#                 "text_to_type": None,
#                 "value": None,
#                 "metadata": {}  # Missing URL
#             }
            
#             result = await session.call_tool(
#                 "execute_action",
#                 {"ui_action": invalid_action}
#             )
#             print("Result:")
#             for content in result.content:
#                 if hasattr(content, 'text'):
#                     print(content.text)
#             print()
            
#             # Test 2: Malformed action data
#             print("Test 2: Malformed action data")
#             malformed_action = {
#                 "type": "click",
#                 # Missing required fields
#             }
            
#             result = await session.call_tool(
#                 "execute_action",
#                 {"ui_action": malformed_action}
#             )
#             print("Result:")
#             for content in result.content:
#                 if hasattr(content, 'text'):
#                     print(content.text)
#             print()
            
#             # Test 3: Invalid tool name
#             print("Test 3: Invalid tool name")
#             result = await session.call_tool(
#                 "invalid_tool_name",
#                 {}
#             )
#             print("Result:")
#             for content in result.content:
#                 if hasattr(content, 'text'):
#                     print(content.text)
#             print()
            
#             print("=== Error Handling Test Complete ===")


if __name__ == "__main__":
    # Run the comprehensive test
    asyncio.run(test_mcp_server_comprehensive()) 