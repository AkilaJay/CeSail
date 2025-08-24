"""
FastMCP Server for dom_parser with basic APIs for web automation.
"""

import asyncio
import json
import ast
from pathlib import Path
from typing import Dict, Any, Optional
from fastmcp import FastMCP
from pydantic import BaseModel
import sys
from pathlib import Path

# Add the parent directory to the path so we can import dom_parser
sys.path.append(str(Path(__file__).parent.parent))

from cesail.dom_parser.src import DOMParser, Action
import logging

logger = logging.getLogger(__name__)

def parse_params(params):
    # If params is already a dict (Cursor sent it correctly), just return it
    if isinstance(params, dict):
        return params
    
    # If it's a JSON string, parse normally
    if isinstance(params, str):
        try:
            return json.loads(params)
        except json.JSONDecodeError:
            # If it's a Python dict string, parse with ast.literal_eval (safe)
            try:
                return ast.literal_eval(params)
            except (ValueError, SyntaxError):
                raise ValueError(f"Invalid params format: {params}")
    
    raise TypeError(f"Unsupported params type: {type(params)}")

# --------------------------------------------------
# FastMCP instance
# --------------------------------------------------
mcp = FastMCP(
    name="dom_parser",
    version="1.0.0",
    instructions="""
    DOM Parser MCP Server for web automation and analysis.
    
    This server provides tools to:
    - Execute actions on web pages (click, type, navigate, scroll, wait)
    - Analyze web pages and extract structured data
    - Capture screenshots of web pages
    
    ENFORCED PATTERN:
    - First call can be any action (execute_action, get_page_details, etc.)
    - After the first action, you MUST follow this pattern:
      1. Call get_page_details to analyze the current page state
      2. Then call execute_action to perform an action
    - This ensures the page is always analyzed before executing actions
    
    Usage Guidelines:
    - Always navigate to a page first before executing actions
    - Use get_page_details to understand the page structure
    - Actions require element IDs which can be found in page analysis
    - The server maintains browser session across multiple calls
    - Screenshots are returned as base64-encoded PNG images
    
    IMPORTANT: When executing actions, use the exact format from available_action_types:
    - The available_action_types from get_page_details shows the exact parameter structure
    - Each action type has specific required parameters (element_id, text_to_type, url, etc.)
    - Always check the available_action_types to see what parameters are needed
    - Use the exact parameter names and types shown in available_action_types
    
    Example workflow:
    1. Call get_page_details to analyze the page
    2. Look at available_action_types to see exact parameter formats
    3. Use execute_action with the exact format from available_action_types
    4. Repeat: get_page_details → execute_action
    """
)

# --------------------------------------------------
# Shared state
# --------------------------------------------------
dom_parser: Optional[DOMParser] = None
last_action_was_get_page_details: bool = False
has_executed_any_action: bool = False

# --------------------------------------------------
# Input models
# --------------------------------------------------
class ExecuteActionInput(BaseModel):
    ui_action: Dict[str, Any]

class GetPageDetailsInput(BaseModel):
    headless: bool = False


# --------------------------------------------------
# Tools
# --------------------------------------------------
@mcp.tool()
async def execute_action(params: Dict[str, Any]) -> str:
    """Execute an action on the current page."""
    global dom_parser, last_action_was_get_page_details, has_executed_any_action
    try:
        # Check if we need to enforce the pattern
        if has_executed_any_action and not last_action_was_get_page_details:
            return json.dumps({
                "error": "Pattern violation: execute_action must be preceded by get_page_details. Please call get_page_details first.",
                "required_action": "get_page_details"
            }, indent=2)
            
        if not dom_parser:
            dom_parser = DOMParser(headless=False)
            await dom_parser.__aenter__()

        logger.error("Executing action...")
        action = Action.from_json(params)

        result = await dom_parser.execute_action(
            action,
            wait_for_idle=True,
            translate_element_id=True
        )
        
        # Update state after successful execution
        has_executed_any_action = True
        last_action_was_get_page_details = False
        
        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Error executing action: {str(e)}"


@mcp.tool()
async def get_page_details(params: Dict[str, Any]) -> str:
    """Analyze the current web page and return details."""
    global dom_parser, last_action_was_get_page_details
    
    # Accept params directly as a dict
    headless = params.get('headless', False)

    try:
        if not dom_parser:
            dom_parser = DOMParser(headless=headless)
            await dom_parser.__aenter__()

        logger.error("Analyzing page...")
        parsed_page = await dom_parser.analyze_page()
        site_actions = getattr(parsed_page, 'actions', [])

        # screenshot_path = Path("/tmp/dom_parser_screenshot.png")
        # screenshot = await dom_parser.take_screenshot(
        #     screenshot_path,
        #     full_page=True,
        #     return_base64=True
        # )

        site_details = {
            "url": parsed_page.metadata.url,
            "title": parsed_page.metadata.title,
            "parsed_actions": site_actions.to_json() if hasattr(site_actions, 'to_json') else site_actions,
        }
        
        # Update state after successful analysis
        last_action_was_get_page_details = True
        
        return json.dumps(site_details, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
async def get_available_actions(params: Dict[str, Any]) -> str:
    """Get available actions for the current web page."""
    global dom_parser
    
    # Accept params directly as a dict
    headless = params.get('headless', False)

    try:
        if not dom_parser:
            dom_parser = DOMParser(headless=headless)
            await dom_parser.__aenter__()

        available_actions = dom_parser.get_available_actions()

        return json.dumps(available_actions, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_screenshot(params: Dict[str, Any]) -> str:
    """Get a screenshot of the current web page."""
    global dom_parser
    
    # Accept params directly as a dict
    headless = params.get('headless', False)

    try:
        if not dom_parser:
            dom_parser = DOMParser(headless=headless)
            await dom_parser.__aenter__()

        screenshot_path = Path("/tmp/dom_parser_screenshot.png")
        screenshot = await dom_parser.take_screenshot(
            screenshot_path,
            full_page=True,
            return_base64=True
        )

        site_details = {
            "screenshot": {
                "data": screenshot,
                "mime_type": "image/png",
                "encoding": "base64"
            }
        }
        return json.dumps(site_details, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
async def reset_pattern_state(params: Dict[str, Any]) -> str:
    """Reset the enforced pattern state. Use this to start fresh or if you get stuck."""
    global last_action_was_get_page_details, has_executed_any_action
    
    last_action_was_get_page_details = False
    has_executed_any_action = False
    
    return json.dumps({
        "message": "Pattern state reset successfully. You can now make any first call.",
        "state": {
            "last_action_was_get_page_details": last_action_was_get_page_details,
            "has_executed_any_action": has_executed_any_action
        }
    }, indent=2)

# --------------------------------------------------
# Main entrypoint
# --------------------------------------------------
if __name__ == "__main__":
    mcp.run()
