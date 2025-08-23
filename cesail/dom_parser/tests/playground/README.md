# Playground: Experimental DOM Parser Integration Tests

This directory contains **experimental integration tests** for the DOM parser, focused on parsing and navigating popular real-world sites. These tests are not strict regression tests, but are used for manual and exploratory testing of the parser’s capabilities and behaviors on complex, dynamic web pages.

## What these tests do

- **Navigate to real sites** (e.g., Google Flights, Pinterest, Amazon, YouTube, Airbnb, NY Times, New Balance, Google Forms, etc.).
- **Use the `DOMParser`** to analyze the page, extract elements, actions, and forms.
- **Optionally execute actions** (like clicking, typing, scrolling) and observe the effects.
- **Print analysis results** (number of elements, actions, forms, etc.) and sometimes take screenshots or visualize elements.
- **Some tests** inject custom JS (like a visualizer) or interact with the page in a loop for debugging.
- **All tests** are meant for manual, interactive, or visual inspection, not for automated CI regression.

## How to run

From the project root, you can run any test in this directory, for example:

```bash
PYTHONPATH=. pytest dom_parser/tests/playground/test_page_analyzer_integration_google.py -v
```

Or run all playground tests:

```bash
PYTHONPATH=. pytest dom_parser/tests/playground/ -v
```

- Many tests open a real browser window (`headless=False`) and may require user interaction or manual inspection.
- Some tests may require a local server (e.g., `test_page_analyzer_integration.py` uses `http://localhost:3001/`).

## Adding new playground tests

- Copy an existing test as a template.
- Change the URL and actions as needed.
- Use these tests to debug, visualize, or experiment with new parser features.

## Notes

- These tests are **not** intended for CI or strict regression.
- They are for **exploration, debugging, and development**.
- If you want to add a new site, just add a new test file following the existing pattern. 
