import pytest
import os
import json
from dom_parser.src.dom_parser import DOMParser

GOLDEN_DIR = os.path.join(os.path.dirname(__file__), "golden_values")

# Find all .dom.html files in the golden_values directory
SITES = [
    fname.replace(".dom.html", "")
    for fname in os.listdir(GOLDEN_DIR)
    if fname.endswith(".dom.html")
]

# Per-site fields to ignore in comparison
IGNORE_FIELDS = {
    "amazon_com": ["data-csa-c-id"],
    # Add more site-specific fields as needed
}

def remove_ignored_fields(obj, ignore_fields):
    if isinstance(obj, dict):
        return {k: remove_ignored_fields(v, ignore_fields) for k, v in obj.items() if k not in ignore_fields}
    elif isinstance(obj, list):
        return [remove_ignored_fields(item, ignore_fields) for item in obj]
    else:
        return obj

@pytest.mark.asyncio
@pytest.mark.parametrize("site_name", SITES)
async def test_golden_replay(site_name):
    dom_file = os.path.join(GOLDEN_DIR, f"{site_name}.dom.html")
    golden_file = os.path.join(GOLDEN_DIR, f"{site_name}.golden.json")
    assert os.path.exists(dom_file), f"DOM file missing: {dom_file}"
    assert os.path.exists(golden_file), f"Golden file missing: {golden_file}"

    with open(dom_file, "r", encoding="utf-8") as f:
        dom = f.read()
    with open(golden_file, "r", encoding="utf-8") as f:
        golden = json.load(f)

    async with DOMParser() as parser:
        await parser.page.set_content(dom)
        parsed = await parser.analyze_page()

    parsed_json = parsed if isinstance(parsed, dict) else parsed.dict() if hasattr(parsed, "dict") else json.loads(json.dumps(parsed))

    ignore_fields = IGNORE_FIELDS.get(site_name, [])
    if ignore_fields:
        parsed_json = remove_ignored_fields(parsed_json, ignore_fields)
        golden = remove_ignored_fields(golden, ignore_fields)

    assert parsed_json == golden, f"Parsed output for {site_name} does not match golden file!" 