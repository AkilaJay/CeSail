import pytest
import json
import os
import asyncio

from dom_parser.src import DOMParser, Action, ActionType

# Enable Playwright debug logging
os.environ["DEBUG"] = "pw:api"

@pytest.mark.asyncio
async def test_dom_parser_integration():
    """Test the DOMParser's ability to get elements and execute actions on Google."""
    async with DOMParser(headless=False) as parser:
        # Get the page and set up console listener
        page = await parser.get_page()
        page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))
        
        # Navigate to Google
        action = Action(
            type=ActionType.NAVIGATE,
            metadata={"url": "https://www.google.com"}
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

        # Type search query
        action = Action(
            type="type",
            element_id="#APjFqb",
            text_to_type="Best food in the bay area"
        )
        
        print("\nExecuting action: Type search query")
        result = await parser.execute_action(action, wait_for_idle=True)
        await parser.take_screenshot("/tmp/03_after_typing.png")
        
        # Re-analyze page after typing
        parsed_page = await parser.analyze_page()

        # Click search button
        action = Action(
            type="click",
            element_id="body:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(3) > form:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(2) > div:nth-of-type(4) > div:nth-of-type(6) > center:nth-of-type(1) > input:nth-of-type(1)"
        )

        print("\nExecuting action: Click search button")
        result = await parser.execute_action(action, wait_for_idle=True)
        await parser.take_screenshot("/tmp/04_after_search.png")

        # Re-analyze page after search
        parsed_page = await parser.analyze_page()

        # Perform multiple scroll actions to see search results
        for i in range(3):
            action = Action(
                type="scroll_down_viewport"
            )
            
            print(f"\nExecuting action: Scroll down the page (scroll #{i+1})")
            result = await parser.execute_action(action, wait_for_idle=True)
            
            # Take screenshot after scroll
            screenshot_path = f"/tmp/{i+5:02d}_after_scroll_{i+1}.png"
            await parser.take_screenshot(screenshot_path)

            # Re-analyze page after scroll
            parsed_page = await parser.analyze_page()

        # Take final screenshot
        await parser.take_screenshot("/tmp/08_final_state.png")

if __name__ == "__main__":
    asyncio.run(test_dom_parser_integration()) 