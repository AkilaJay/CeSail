import pytest
import json
import os
import time
import asyncio

from dom_parser.src import DOMParser, Action, ActionType

# Enable Playwright debug logging
os.environ["DEBUG"] = "pw:api"

@pytest.mark.asyncio
async def test_dom_parser_integration():
    """Test the DOMParser's ability to get elements and execute actions."""
    async with DOMParser(headless=False) as parser:
        # Get the page and set up console listener
        page = await parser.get_page()
        # page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))
        
        # Navigate to Pinterest
        action = Action(
            type=ActionType.NAVIGATE,
            metadata={"url": "https://www.pinterest.com/ideas/"}
        )
        await parser._action_executor.execute_action(action)
        
        # Take screenshot after navigation
        await parser.take_screenshot("/tmp/01_after_navigation.png")

        # Analyze the page
        print("\nAnalyzing page...")
        parsed_page = await parser.analyze_page()
        
        # Take screenshot after analysis
        await parser.take_screenshot("/tmp/02_after_analysis.png")
        
        # Print page analysis results
        print("\nPage Analysis Results:")
        print(f"URL: {parsed_page.metadata.url}")
        print(f"Number of elements: {len(parsed_page.important_elements.elements)}")
        print(f"Number of forms: {len(parsed_page.forms.forms)}")
        print(f"Number of actions: {len(parsed_page.actions.actions)}")

        print("Available actions:")
        print(json.dumps(parsed_page.to_json()["actions"], indent=2))

        print("Testing selector functionality:")
        selector = await parser.page_analyzer.get_selector_by_id("1")
        print(f"Selector for element 1: {selector}")

        # Perform multiple scroll actions
        for i in range(7):
            action = Action(
                type="scroll_down_viewport"
            )
            
            print(f"\nExecuting action: {action.description}")
            result = await parser.execute_action(action, wait_for_idle=True)
            
            # Take screenshot after scroll
            screenshot_path = f"/tmp/{i+3:02d}_after_scroll_{i+1}.png"
            await parser.take_screenshot(screenshot_path)

            # Re-analyze page after scroll
            parsed_page = await parser.analyze_page()
            
            # Special handling for scroll #3 (base64 screenshot test)
            if i == 2:
                print("Testing base64 screenshot...")
                screenshot = await parser.take_screenshot(
                    filepath="/tmp/05_screenshot_base64.png",
                    quality=None,
                    format="png",
                    full_page=False,
                    return_base64=True
                )
                print(f"Base64 screenshot length: {len(screenshot) if screenshot else 0}")

        # Take final screenshot
        await parser.take_screenshot("/tmp/11_final_state.png")

if __name__ == "__main__":
    asyncio.run(test_dom_parser_integration()) 