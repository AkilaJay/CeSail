#!/usr/bin/env python3
"""
Quick test of CeSail installation following README quickstart example
"""

import asyncio
from cesail import DOMParser, Action, ActionType

async def test_quickstart():
    """Test the basic DOMParser functionality"""
    print("🚀 Testing CeSail Quickstart...")
    
    # Initialize DOMParser with context manager (recommended)
    async with DOMParser(headless=False) as parser:
        try:
            # Navigate to a website
            print("📄 Navigating to example.com...")
            action = Action(
                type=ActionType.NAVIGATE,
                metadata={"url": "https://www.example.com"}
            )
            await parser._action_executor.execute_action(action)
            
            # Analyze the page and get structured data
            print("🔍 Analyzing page...")
            parsed_page = await parser.analyze_page()
            print("✅ Successfully parsed page")
            print(f"📊 Found {len(parsed_page.actions.actions)} interactive elements")
            
            # Take a screenshot with overlays
            print("📸 Taking screenshot...")
            await parser.take_screenshot("demo_screenshot.png")
            
            # Show available actions
            print("🎯 Available actions:")
            for element in parsed_page.actions.actions[:3]:
                print(f"  - {element.type}: {element.selector}")
            
            print("✅ Quickstart test completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during quickstart test: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(test_quickstart())
