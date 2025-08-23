import pytest
import json
import os
import asyncio

from dom_parser.src import DOMParser, Action, ActionType

# Enable Playwright debug logging
os.environ["DEBUG"] = "pw:api"

@pytest.mark.asyncio
async def test_dom_parser_integration():
    """Test the DOMParser's ability to get elements and execute actions on YouTube."""
    async with DOMParser(headless=False) as parser:
        # Get the page and set up console listener
        page = await parser.get_page()
        page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))
        
        # Navigate to YouTube
        action = Action(
            type=ActionType.NAVIGATE,
            metadata={"url": "https://www.youtube.com"}
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

        # Click on Shorts tab
        action = Action(
            type="click",
            element_id="role=tab[name=\"Shorts\"]"
        )
        
        print("\nExecuting action: Click on Shorts tab")
        result = await parser.execute_action(action, wait_for_idle=True)
        await parser.take_screenshot("/tmp/03_after_shorts_click.png")

        # There is a bug in the observer that sometimes causes it to not wait for the page to be idle
        # so we need to wait for a bit to make sure the page is idle
        await asyncio.sleep(3)
        
        # Re-analyze page after clicking Shorts
        parsed_page = await parser.analyze_page()

        # Perform multiple navigation actions
        for i in range(3):
            action = Action(
                type="click",
                element_id="body:nth-of-type(1) > ytd-app:nth-of-type(1) > div:nth-of-type(1) > ytd-page-manager:nth-of-type(1) > ytd-shorts:nth-of-type(1) > div:nth-of-type(5) > div:nth-of-type(2) > ytd-button-renderer:nth-of-type(1) > yt-button-shape:nth-of-type(1) > button:nth-of-type(1)"
            )

            print(f"\nExecuting action: Navigate down (navigation #{i+1})")
            result = await parser.execute_action(action, wait_for_idle=False)

            await asyncio.sleep(2)
            
            # Re-analyze page after navigation
            parsed_page = await parser.analyze_page()

        # Take final screenshot
        await parser.take_screenshot("/tmp/07_final_state.png")

if __name__ == "__main__":
    asyncio.run(test_dom_parser_integration()) 