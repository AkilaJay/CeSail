import os
import json
import pytest
from dom_parser.src.dom_parser import DOMParser
from dom_parser.src.py.types import Action, ActionType

REPLAY_DIR = os.path.dirname(__file__)
GOLDEN_DIR = REPLAY_DIR

SITES = [
    {
        "name": "example_com",
        "url": "https://example.com",
    },
    {
        "name": "pinterest_com",
        "url": "https://www.pinterest.com",
    },
    {
        "name": "amazon_com",
        "url": "https://www.amazon.com",
    },
]

@pytest.mark.asyncio
@pytest.mark.parametrize("site", SITES)
async def test_generate_golden(site):
    golden_file = os.path.join(GOLDEN_DIR, f"{site['name']}.golden.json")
    dom_file = os.path.join(GOLDEN_DIR, f"{site['name']}.dom.html")
    os.makedirs(GOLDEN_DIR, exist_ok=True)

    # Always delete and regenerate the DOM and golden files
    if os.path.exists(dom_file):
        os.remove(dom_file)
    if os.path.exists(golden_file):
        os.remove(golden_file)

    # Step 1: Fetch and save DOM using Action-based navigation
    async with DOMParser() as parser:
        action = Action(
            type=ActionType.NAVIGATE,
            metadata={"url": site["url"]}
        )
        await parser._action_executor.execute_action(action)
        dom = await parser.page.content()
        with open(dom_file, "w", encoding="utf-8") as f:
            f.write(dom)

    # Step 2: Parse and generate golden output from the saved DOM
    with open(dom_file, "r", encoding="utf-8") as f:
        dom = f.read()
    async with DOMParser() as parser:
        await parser.page.set_content(dom)
        parsed = await parser.analyze_page()

    parsed_json = parsed if isinstance(parsed, dict) else parsed.dict() if hasattr(parsed, "dict") else json.loads(json.dumps(parsed))
    with open(golden_file, "w", encoding="utf-8") as f:
        json.dump(parsed_json, f, indent=2, ensure_ascii=False)
    # Always skip to indicate regeneration
    pytest.skip(f"Golden file regenerated for {site['name']}. Rerun to compare.") 