# Replay-Based Golden Testing

This directory contains tests and scripts for replay-based regression testing of the DOM parser.

## What is this?
- For each site, we save a snapshot of the DOM (`.dom.html`) and the expected parsed output (`.golden.json`).
- The replay test loads the saved DOM, parses it with the current DOM parser, and compares the result to the golden JSON.
- This protects the parser implementation from accidental regressions.

## How to Run the Replay Test

From the project root:

```bash
PYTHONPATH=. pytest dom_parser/tests/replay_tests/test_golden_replay.py -v
```

- This will parse each `.dom.html` in `golden_values/` and compare to the corresponding `.golden.json`.
- If the outputs differ, the test will fail and show a diff.

## How to Regenerate Goldens

To update the DOM and golden files for all sites:

```bash
PYTHONPATH=. pytest dom_parser/tests/replay_tests/golden_values/generate_golden_example_com.py -v
```

- This will delete and regenerate both the `.dom.html` and `.golden.json` for each site listed in the script.
- The test will always be skipped after regeneration; rerun the replay test to check for stability.

## Adding a New Site
1. Add a new entry to the `SITES` list in `generate_golden_example_com.py` with the site name and URL.
2. Run the golden generation script as above.
3. The new site's DOM and golden files will appear in `golden_values/`.
4. The replay test will automatically pick up the new site.

## Handling Dynamic Fields
- Some sites (like Amazon) include dynamic fields (e.g., tracking IDs) that change on every page load.
- To ignore these fields in the comparison, add them to the `IGNORE_FIELDS` dictionary in `test_golden_replay.py`.
- The test will recursively remove these fields from both the parsed output and the golden file before comparison.

## Notes
- Do **not** edit `.dom.html` or `.golden.json` files by hand.
- Always regenerate goldens using the script to ensure consistency.
- If you want to update goldens for a site, simply rerun the generation script. 