# DOM Parser Python Layer

Orchestration layer that manages browser interactions and provides high-level APIs.

## Overview

The Python layer serves as the orchestration and integration layer for CeSail's DOM parsing capabilities. It manages browser interactions, provides high-level APIs, and coordinates between the JavaScript parsing engine and external consumers like the MCP server.

## Key Components

### Core Files

- **`dom_parser.py`**: Main interface for DOM parsing and interaction
- **`page_analyzer.py`**: Analyzes page structure and extracts actionable elements
- **`action_executor.py`**: Executes web actions through Playwright
- **`idle_watcher.py`**: Monitors page state and waits for stability
- **`screenshot.py`**: Captures and processes page screenshots
- **`types.py`**: Data structures and type definitions
- **`config.py`**: Configuration management and validation

### Action Plugins (`actions_plugins/`)

- **`navigation_actions.py`**: Navigate, back, forward, switch tabs
- **`interaction_actions.py`**: Click, hover, scroll, drag & drop
- **`input_actions.py`**: Type, select, check, clear, upload
- **`system_actions.py`**: Wait, alerts, screenshots
- **`base_action.py`**: Base class for all actions

## Features

- **Page Analysis**: Comprehensive page structure analysis and element extraction
- **Action Execution**: Executes clicks, typing, navigation, and other web actions
- **Idle Watching**: Monitors page state changes and waits for stability
- **Screenshot Integration**: Captures and analyzes visual page content
- **Configuration Management**: Flexible configuration for different use cases
- **Session Management**: Maintains browser state across interactions
- **Error Handling**: Robust error recovery and retry logic

## Usage

### Basic Usage

```python
import asyncio
from dom_parser.src.dom_parser import DOMParser

async def basic_example():
    async with DOMParser() as parser:
        # Navigate to page
        await parser.navigate("https://example.com")
        
        # Analyze page structure
        parsed_page = await parser.analyze_page()
        
        # Execute actions
        await parser.click("button.btn-primary")
        await parser.type("input#email", "user@example.com")
```

### Advanced Configuration

```python
config = {
    "browser": {
        "headless": False,
        "browser_type": "chromium"
    },
    "idle_watcher": {
        "default_idle_time_ms": 500
    }
}

async with DOMParser(config=config) as parser:
    # Your automation code here
    pass
```

## Architecture

The Python layer provides:

1. **Browser Management**: Launches and manages Playwright browser instances
2. **JavaScript Injection**: Injects the DOM parsing JavaScript into web pages
3. **Action Orchestration**: Coordinates action execution through Playwright
4. **State Management**: Maintains browser state and session information
5. **Error Recovery**: Handles errors and provides retry mechanisms
6. **API Integration**: Provides clean APIs for external consumers

## Integration

The Python layer integrates with:

- **MCP Server**: Provides standardized APIs for AI agents
- **Simple Agent**: Enables LLM-powered web automation
- **Playwright**: Browser automation and control
- **JavaScript Layer**: DOM parsing and element extraction

## Configuration

The Python layer supports extensive configuration options:

- Browser settings (headless, type, arguments)
- Idle watching parameters
- Action execution timeouts
- Screenshot settings
- Logging and debugging options

## Error Handling

Robust error handling includes:

- Network timeout recovery
- Element not found retries
- Browser crash recovery
- JavaScript execution error handling
- Graceful degradation for unsupported features
