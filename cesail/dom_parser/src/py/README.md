# DOM Parser Python Layer

Orchestration layer that manages browser interactions and provides high-level APIs for AI-powered web automation.

## Overview

The Python layer serves as the orchestration and integration layer for CeSail's DOM parsing capabilities. It manages browser interactions, provides high-level APIs, and coordinates between the JavaScript parsing engine and external consumers like the MCP server.

## Core Components

### DOMParser Class

The top-level interface for DOM parsing and web automation. This is the main entry point that orchestrates all functionality including page analysis, action execution, and screenshot capture.

```python
from cesail.dom_parser.src import DOMParser

# Basic initialization
parser = DOMParser()

# With custom configuration
config = {
    "browser": {"headless": True},
    "idle_watcher": {"default_idle_time_ms": 500}
}
parser = DOMParser(config=config)

# Context manager usage (recommended)
async with DOMParser() as parser:
    # Your automation code here
    pass
```

#### Supported APIs

**Core Methods:**
- `analyze_page() -> ParsedPage` - Analyze current page and return structured data
- `execute_action(action, wait_for_idle=True, translate_element_id=False) -> ActionResult` - Execute web actions
- `take_screenshot(filepath, dimensions=None, quality=None, format=None, full_page=False, clip=None, omit_background=False, return_base64=False) -> str` - Capture screenshots

**Page Management:**
- `get_page() -> Page` - Get the current Playwright page instance
- `get_page_content() -> str` - Get current page's HTML content

**Component Access (Properties):**
- `page_analyzer -> PageAnalyzer` - Access page analysis functionality
- `action_executor -> ActionExecutor` - Access action execution functionality  
- `screenshot_taker -> ScreenshotTaker` - Access screenshot functionality

**Configuration & Information:**
- `get_available_actions() -> Dict[str, Any]` - Get list of all available actions and parameters

**Context Management:**
- `__aenter__()` - Initialize browser and page (called automatically with `async with`)
- `__aexit__()` - Clean up resources (called automatically with `async with`)

### PageAnalyzer

Analyzes page structure and extracts actionable elements. Provides comprehensive page analysis capabilities including element extraction, selector management, and action generation.

```python
# Get page analysis
parsed_page = await parser.analyze_page()

# Access different components
actions = parsed_page.get_actions()
forms = parsed_page.get_forms()
metadata = parsed_page.get_metadata()
elements = parsed_page.get_important_elements()

# Get selector mapping
selector_map = await parser.page_analyzer.get_selector_mapping()
selector = await parser.page_analyzer.get_selector_by_id("1")
```

#### Supported APIs

**Core Analysis:**
- `analyze_page() -> ParsedPage` - Analyze current page and return comprehensive structured data

**Selector Management:**
- `get_selector_mapping() -> Dict[str, str]` - Get complete mapping between selector IDs and original selectors
- `get_selector_by_id(selector_id: str) -> Optional[str]` - Get original selector string from selector ID
- `get_selector_id(selector: str) -> Optional[str]` - Get selector ID from original selector string
- `clear_selector_mapping() -> None` - Clear the selector mapping cache

**Processing Pipeline Access:**
- `get_raw_actions() -> List[Dict[str, Any]]` - Get raw actions from processing pipeline
- `get_grouped_actions() -> List[Dict[str, Any]]` - Get grouped actions from processing pipeline
- `get_scored_actions() -> List[Dict[str, Any]]` - Get scored actions from processing pipeline
- `get_transformed_actions() -> List[Dict[str, Any]]` - Get transformed actions from processing pipeline
- `get_filtered_actions() -> List[Dict[str, Any]]` - Get filtered actions from processing pipeline
- `get_mapped_actions() -> List[Dict[str, Any]]` - Get mapped actions from processing pipeline
- `get_field_filtered_actions() -> List[Dict[str, Any]]` - Get field filtered actions from processing pipeline

### ActionExecutor

Executes web actions through Playwright using a plugin-based architecture. Supports a comprehensive set of web automation actions organized into categories.

```python
from cesail.dom_parser.src.py.types import Action, ActionType

# Navigation actions
navigate_action = Action(
    type=ActionType.NAVIGATE,
    metadata={"url": "https://example.com"}
)

back_action = Action(type=ActionType.BACK)
forward_action = Action(type=ActionType.FORWARD)

# Interaction actions
click_action = Action(
    type=ActionType.CLICK,
    element_id="button.submit"
)

type_action = Action(
    type=ActionType.TYPE,
    element_id="input#email",
    text_to_type="user@example.com"
)

hover_action = Action(
    type=ActionType.HOVER,
    element_id="button.dropdown"
)

# Scrolling actions
scroll_action = Action(type=ActionType.SCROLL_DOWN_VIEWPORT)

scroll_by_action = Action(
    type=ActionType.SCROLL_BY,
    metadata={"x": 0, "y": 500}
)

# Execute actions
result = await parser.execute_action(action, wait_for_idle=True)
```

#### Supported Action Plugins

**Navigation Actions** (`navigation_actions.py`):
- `NavigateAction` - Navigate to a URL
- `BackAction` - Go back in browser history
- `ForwardAction` - Go forward in browser history
- `SwitchTabAction` - Switch to a different tab
- `CloseTabAction` - Close the current tab
- `SwitchToFrameAction` - Switch to an iframe
- `SwitchToParentFrameAction` - Switch back to parent frame

**Interaction Actions** (`interaction_actions.py`):
- `ClickAction` - Click on an element
- `RightClickAction` - Right-click on an element
- `DoubleClickAction` - Double-click on an element
- `HoverAction` - Hover over an element
- `FocusAction` - Focus on an element
- `BlurAction` - Remove focus from an element
- `ScrollToAction` - Scroll to a specific element
- `ScrollByAction` - Scroll by specific amount
- `ScrollDownViewportAction` - Scroll down the viewport
- `DragDropAction` - Drag and drop elements

**Input Actions** (`input_actions.py`):
- `TypeAction` - Type text into an input field
- `CheckAction` - Check/uncheck checkboxes and radio buttons
- `SelectAction` - Select options from dropdowns
- `ClearAction` - Clear input field content
- `PressKeyAction` - Press keyboard keys
- `KeyDownAction` - Hold down a key
- `KeyUpAction` - Release a key
- `UploadFileAction` - Upload files
- `SubmitAction` - Submit forms
- `DatePickAction` - Select dates from date pickers
- `SliderAction` - Adjust slider values

**System Actions** (`system_actions.py`):
- `AlertAcceptAction` - Accept browser alerts
- `AlertDismissAction` - Dismiss browser alerts
- `WaitAction` - Wait for a specified time
- `WaitForSelectorAction` - Wait for an element to appear
- `WaitForNavigationAction` - Wait for page navigation

#### Supported APIs

**Core Execution:**
- `execute_action(action: Action) -> Dict[str, Any]` - Execute a single action
- `execute_actions(actions: List[Action]) -> List[Dict[str, Any]]` - Execute multiple actions in sequence
- `execute_action_from_json(action_json: Dict[str, Any]) -> Dict[str, Any]` - Execute action from JSON

**Configuration & Information:**
- `get_available_actions() -> Dict[str, Any]` - Get comprehensive information about all available action plugins
- `_get_action_plugin(action_type: ActionType) -> Optional[Type[BaseAction]]` - Get plugin class for action type

#### Action Plugin Architecture

All action plugins inherit from `BaseAction` which provides:

- **`action_type`** - Property defining the action type
- **`execute(action)`** - Abstract method for action implementation
- **`_get_element(element_id)`** - Helper to get visible elements
- **`_create_success_result()`** - Helper for success responses
- **`_create_error_result()`** - Helper for error responses

**Extending Actions:** You can add custom actions by creating new action classes in the `actions_plugins/` directory and registering them in the ActionExecutor.

### ScreenshotTaker

Handles screenshot capture with configurable dimensions, quality, and coordinate conversion capabilities. **The primary use case is to draw bounding boxes on the browser with selector IDs, take a screenshot, and send it to an LLM for visual analysis and action planning.**

```python
# Basic screenshot
await parser.take_screenshot("screenshot.png")

# Screenshot with custom dimensions
await parser.take_screenshot(
    filepath="custom_size.png",
    dimensions=(1920, 1080)
)

# High quality JPEG
await parser.take_screenshot(
    filepath="high_quality.jpg",
    format="jpeg",
    quality=95
)

# Full page screenshot
await parser.take_screenshot(
    filepath="full_page.png",
    full_page=True
)

# Base64 screenshot
base64_screenshot = await parser.take_screenshot(
    filepath="screenshot.png",
    return_base64=True
)
```

#### Supported APIs

**Core Screenshot:**
- `take_screenshot(filepath, dimensions=None, quality=None, format=None, full_page=False, clip=None, omit_background=False, return_base64=False) -> str` - Take screenshot with configurable parameters

**Coordinate Conversion:**
- `convert_coordinates(x, y, from_resolution, to_resolution) -> Tuple[float, float]` - Convert coordinates between resolutions
- `convert_coordinates_from_screenshot_to_actual(x, y) -> Tuple[float, float]` - Convert from screenshot to actual page coordinates
- `convert_coordinates_from_actual_to_screenshot(x, y) -> Tuple[float, float]` - Convert from actual page to screenshot coordinates

**Viewport Management:**
- `get_viewport_info() -> Dict[str, Any]` - Get stored viewport information
- `_store_viewport_info(dimensions=None)` - Store viewport size information

#### Features

- **Multiple Formats**: PNG, JPEG, WebP support
- **Quality Control**: Configurable JPEG quality (1-100)
- **Dimension Control**: Resize page before screenshot
- **Coordinate Conversion**: Convert between different resolutions
- **Full Page Capture**: Capture entire page content
- **Clipping Support**: Capture specific regions
- **Base64 Output**: Return base64 encoded images
- **Background Control**: Transparent PNG support

#### Configuration

```python
config = {
    "screenshot": {
        "default_format": "png",    # Default image format
        "default_quality": 90       # Default JPEG quality
    }
}
```

#### Parameters

- **`filepath`**: Path to save the screenshot
- **`dimensions`**: Tuple of (width, height) to resize page
- **`quality`**: JPEG quality (1-100), only for JPEG format
- **`format`**: Image format ('jpeg', 'png', 'webp')
- **`full_page`**: Whether to capture entire page
- **`clip`**: Dict with x, y, width, height for clipping
- **`omit_background`**: Create transparent PNG
- **`return_base64`**: Return base64 string instead of filepath

### IdleWatcher

Monitors page state and waits for stability before proceeding with actions. Uses efficient DOM mutation detection and viewport-aware analysis. The component implements a MutationObserver to watch for DOM changes and waits for DOMContentLoaded events. **Note: This component can be buggy and doesn't always reliably wait for complete page load. For critical applications, consider implementing additional wait conditions or manual timeouts.**

```python
from cesail.dom_parser.src.py.idle_watcher import wait_for_page_ready, wait_for_page_quiescence

# Wait for page to be ready (Promise-style)
ready_promise = wait_for_page_ready(page, mutation_timeout_ms=300)
await ready_promise

# Wait for page quiescence with timeout
visible_elements = await wait_for_page_quiescence(
    page, 
    idle_ms=300, 
    timeout_ms=10000
)
```

#### Supported APIs

**Core Functions:**
- `wait_for_page_ready(page, mutation_timeout_ms=300, config=None)` - Create Promise-like object for page readiness
- `wait_for_page_quiescence(page, idle_ms=300, skip_urls=None, timeout_ms=10000, config=None)` - Wait for page stability

**EfficientIdleWatcher Class:**
- `wait_for_dom_content_loaded()` - Wait for DOMContentLoaded event
- `wait_for_visible_mutations()` - Wait for DOM mutations to settle
- `get_visible_actions()` - Get visible interactive elements
- `get_page_state()` - Get current page state with visible actions
- `stop()` - Clean up resources

**ViewportAwareIdleWatcher Class:**
- `wait_for_quiescence(timeout_ms=10000)` - Wait for page to be quiescent
- `get_visible_elements()` - Get all visible interactive elements
- `analyze_page()` - Complete page analysis with viewport info

#### Features

- **Efficient Detection**: Uses DOMContentLoaded + MutationObserver for fast detection
- **Viewport Filtering**: Focuses on elements visible in the current viewport
- **Configurable Timeouts**: Adjustable mutation and network idle timeouts
- **Backward Compatibility**: Maintains compatibility with legacy idle watchers
- **Promise-style API**: Can be used with async/await patterns
```

## Configuration

### Default Configuration

```python
DEFAULT_CONFIG = {
    "browser": {
        "headless": False,
        "browser_type": "chromium",
        "browser_args": [
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--no-sandbox",
            "--enable-logging",
            "--v=1"
        ],
        "context_options": {},
        "extra_http_headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9...",
            "Accept-Language": "en-US,en;q=0.9"
        }
    },
    "action_executor": {
        "enabled_actions": [
            "click", "type", "hover", "select", "check", "clear", "submit",
            "navigate", "back", "forward", "scroll_to", "scroll_by", "scroll_down_viewport",
            "right_click", "double_click", "focus", "blur", "drag_drop",
            "press_key", "key_down", "key_up", "upload_file",
            "alert_accept", "alert_dismiss", "wait", "wait_for_selector", "wait_for_navigation",
            "switch_to_frame", "switch_to_parent_frame", "switch_tab", "close_tab"
        ]
    },
    "idle_watcher": {
        "default_idle_time_ms": 300,
        "mutation_timeout_ms": 5000,
        "network_idle_timeout_ms": 1000,
        "enable_console_logging": True,
        "log_idle_events": False,
        "strict_idle_detection": False
    },
    "page_analyzer": {
        "element_extraction": {
            "extract_forms": True,
            "extract_media": True,
            "extract_links": True,
            "extract_structured_data": True,
            "extract_dynamic_state": True,
            "extract_layout_info": True,
            "extract_pagination_info": True,
            "extract_meta_data": True,
            "extract_document_outline": True,
            "extract_text_content": True,
            "actions": {
                "enable_mapping": True,
                "show_bounding_boxes": True,
                "action_filters": {
                    "include_fields": ["type", "selector", "importantText"],
                    "exclude_fields": [],
                    "important_text_max_length": 250,
                    "trim_text_to_length": 100
                }
            }
        }
    },
    "screenshot": {
        "default_format": "png",
        "default_quality": 90
    },
    "global": {
        "bundle_path": None,
        "enable_console_logging": False, # Prints all JS logs - can be very verbose
        "log_level": "INFO"
    }
}

**For complete configuration options and defaults, see:** `/Users/rachitapradeep/CeSail/dom_parser/src/py/config.py`
```

#### Available Action Filter Fields

The `action_filters.include_fields` configuration controls which fields are included in the extracted action data:

- **`"type"`**: Element type (BUTTON, LINK, INPUT, SELECT, etc.)
- **`"selector"`**: CSS selector for the element (e.g., "button.submit", "input#email")
- **`"importantText"`**: Most important text content including labels, aria-labels, placeholders, and contextual text
- **`"text"`**: Raw text content of the element
- **`"bbox"`**: Bounding box coordinates with x, y, width, height (normalized to viewport)
- **`"attributes"`**: All HTML attributes of the element (class, id, href, etc.)
- **`"score"`**: Importance score of the element (higher = more important)
- **`"object"`**: Internal object reference for advanced usage

**Text Length Limits:**
- `important_text_max_length`: Maximum length for importantText (default: 250)
- `trim_text_to_length`: Maximum length for text field (default: 100)

## Advanced Usage Examples

### Complete Web Automation Workflow

```python
import asyncio
import json
from cesail.dom_parser.src import DOMParser, Action, ActionType

async def complete_workflow():
    async with DOMParser(headless=False) as parser:
        # Navigate to a website
        navigate_action = Action(
            type=ActionType.NAVIGATE,
            metadata={"url": "https://www.pinterest.com/ideas/"}
        )
        await parser._action_executor.execute_action(navigate_action)
        
        # Take initial screenshot
        await parser.take_screenshot("/tmp/01_after_navigation.png")
        
        # Analyze the page
        parsed_page = await parser.analyze_page()
        print(f"URL: {parsed_page.metadata.url}")
        print(f"Elements: {len(parsed_page.important_elements.elements)}")
        print(f"Actions: {len(parsed_page.actions.actions)}")
        
        # Print available actions
        print("Available actions:")
        print(json.dumps(parsed_page.to_json()["actions"], indent=2))
        
        # Test selector functionality
        selector = await parser.page_analyzer.get_selector_by_id("1")
        print(f"Selector for element 1: {selector}")
        
        # Perform scrolling and re-analysis
        for i in range(3):
            scroll_action = Action(type=ActionType.SCROLL_DOWN_VIEWPORT)
            result = await parser.execute_action(scroll_action, wait_for_idle=True)
            
            # Take screenshot after scroll
            await parser.take_screenshot(f"/tmp/scroll_{i+1}.png")
            
            # Re-analyze page
            parsed_page = await parser.analyze_page()
            
            # Test base64 screenshot
            if i == 1:
                screenshot = await parser.take_screenshot(
                    filepath="/tmp/base64_screenshot.png",
                    quality=None,
                    format="png",
                    full_page=False,
                    return_base64=True
                )
                print(f"Base64 screenshot length: {len(screenshot) if screenshot else 0}")

asyncio.run(complete_workflow())
```

### Screenshot and Analysis

```python
async def screenshot_analysis():
    async with DOMParser() as parser:
        # Navigate and analyze
        await parser._action_executor.execute_action(Action(
            type=ActionType.NAVIGATE,
            metadata={"url": "https://example.com"}
        ))
        
        # Take different types of screenshots
        # Regular screenshot
        await parser.take_screenshot("regular.png")
        
        # Full page screenshot
        await parser.take_screenshot(
            filepath="full_page.png",
            full_page=True
        )
        
        # High quality JPEG
        await parser.take_screenshot(
            filepath="high_quality.jpg",
            format="jpeg",
            quality=95
        )
        
        # Base64 screenshot
        base64_screenshot = await parser.take_screenshot(
            return_base64=True,
            format="png"
        )
        
        # Analyze page with different options
        parsed_page = await parser.analyze_page()
        
        # Get specific data
        actions = parsed_page.get_actions()
        forms = parsed_page.get_forms()
        metadata = parsed_page.get_metadata()
        
        # Print results
        print(f"Page title: {metadata.title}")
        print(f"Available actions: {len(actions)}")
        print(f"Forms found: {len(forms)}")
```
