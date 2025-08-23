# CeSail MCP Server

FastMCP server that provides standardized APIs for AI agents to interact with web pages through CeSail's DOM parsing capabilities.

## Overview

The CeSail MCP server bridges the gap between AI agents and web automation by providing clean, predictable APIs for web interaction. It leverages CeSail's advanced DOM parsing to give agents structured, actionable data about web pages.

## Features

- **Structured APIs**: Clean, predictable endpoints for web automation
- **Action Execution**: Execute clicks, typing, navigation based on transformed data
- **Page Analysis**: Get structured page information in agent-friendly format
- **Screenshot Integration**: Visual context combined with structured data
- **Session Management**: Maintain state across interactions
- **Error Handling**: Robust retry logic and error recovery

## Installation

The MCP server is included with CeSail installation. To use it:

```bash
# Install CeSail (includes MCP server)
pip install cesail

# Or install from source
git clone https://github.com/AkilaJay/cesail.git
cd cesail
pip install -e .
```

## Usage

### Starting the Server

```bash
# Start the FastMCP server
python -m cesail.mcp.fastmcp_server
```

### Configuration

Create a `.cursor/mcp.json` file in your project:

```json
{
  "mcpServers": {
    "cesail": {
      "command": "python",
      "args": ["-m", "cesail.mcp.fastmcp_server"],
      "env": {}
    }
  }
}
```

## Available Actions

### Navigation Actions

#### `navigate`
Navigate to a specific URL.

**Parameters**:
- `metadata.url` (string, required): The URL to navigate to

**Example**:
```python
await execute_action({
    "type": "navigate",
    "metadata": {"url": "https://example.com"}
})
```

#### `back`
Navigate back in browser history.

**Example**:
```python
await execute_action({"type": "back"})
```

#### `forward`
Navigate forward in browser history.

**Example**:
```python
await execute_action({"type": "forward"})
```

### Interaction Actions

#### `click`
Click on an element.

**Parameters**:
- `element_id` (string, required): CSS selector or element identifier

**Example**:
```python
await execute_action({
    "type": "click",
    "element_id": "button.submit-btn"
})
```

#### `type`
Type text into an input field.

**Parameters**:
- `element_id` (string, required): CSS selector or element identifier
- `text_to_type` (string, required): Text to type

**Example**:
```python
await execute_action({
    "type": "type",
    "element_id": "input#email",
    "text_to_type": "user@example.com"
})
```

#### `hover`
Hover over an element.

**Parameters**:
- `element_id` (string, required): CSS selector or element identifier

**Example**:
```python
await execute_action({
    "type": "hover",
    "element_id": "button.dropdown"
})
```

### Scrolling Actions

#### `scroll_down_viewport`
Scroll down one viewport height.

**Example**:
```python
await execute_action({"type": "scroll_down_viewport"})
```

#### `scroll_by`
Scroll by a specific amount.

**Parameters**:
- `metadata.x` (number, optional): Horizontal scroll amount
- `metadata.y` (number, optional): Vertical scroll amount

**Example**:
```python
await execute_action({
    "type": "scroll_by",
    "metadata": {"x": 0, "y": 500}
})
```

### Tab Management

#### `switch_tab`
Switch to a different browser tab.

**Parameters**:
- `metadata.tab_index` (number, optional): Tab index to switch to (default: 0)

**Example**:
```python
await execute_action({
    "type": "switch_tab",
    "metadata": {"tab_index": 1}
})
```

#### `close_tab`
Close the current browser tab.

**Example**:
```python
await execute_action({"type": "close_tab"})
```

### System Actions

#### `wait`
Wait for a specified duration.

**Parameters**:
- `metadata.timeout` (number, optional): Timeout in milliseconds

**Example**:
```python
await execute_action({
    "type": "wait",
    "metadata": {"timeout": 2000}
})
```

#### `wait_for_selector`
Wait for an element to appear.

**Parameters**:
- `metadata.selector` (string, optional): CSS selector to wait for
- `metadata.state` (string, optional): Element state ("visible", "hidden", "attached", "detached")
- `metadata.timeout` (number, optional): Timeout in milliseconds

**Example**:
```python
await execute_action({
    "type": "wait_for_selector",
    "metadata": {
        "selector": "button.loaded",
        "state": "visible",
        "timeout": 5000
    }
})
```

## Page Analysis

### `get_page_details`
Get comprehensive information about the current page.

**Returns**: Structured page data including:
- **Actions**: Interactive elements (buttons, links, inputs)
- **Forms**: Form elements and their fields
- **Metadata**: Page title, URL, meta tags
- **Important Elements**: Key page elements with detailed information

**Example Response**:
```json
{
  "url": "https://example.com",
  "title": "Example Page",
  "parsed_actions": [
    {
      "type": "BUTTON",
      "selector": "8",
      "importantText": "Sign up | Sign up"
    },
    {
      "type": "LINK",
      "selector": "2",
      "importantText": "Home | / | Home"
    }
  ]
}
```

## Error Handling

The MCP server includes robust error handling:

- **Network timeouts**: Automatic retry with exponential backoff
- **Element not found**: Clear error messages with suggestions
- **Browser crashes**: Automatic recovery and session restoration
- **Invalid actions**: Validation and helpful error messages

## Integration Examples

### With Cursor

```python
# In Cursor, you can now use natural language
"Navigate to example.com and click the sign up button"
"Fill out the contact form with my information"
"Take a screenshot of the current page"
```

### With Other MCP Clients

```python
# Programmatic usage
from cesail_mcp import FastMCPServer

server = FastMCPServer()
await server.start()

# Execute actions
result = await server.execute_action({
    "type": "navigate",
    "metadata": {"url": "https://example.com"}
})
```

## Configuration Options

### Environment Variables

- `CESAIL_HEADLESS`: Set to "true" to run browser in headless mode
- `CESAIL_TIMEOUT`: Default timeout for actions (default: 30000ms)
- `CESAIL_BROWSER_TYPE`: Browser type to use (default: "chromium")

### Browser Configuration

```python
# Custom browser configuration
config = {
    "browser": {
        "headless": False,
        "browser_type": "chromium",
        "browser_args": ["--no-sandbox"]
    }
}
```

## Troubleshooting

### Common Issues

1. **"Target page closed" error**
   - Solution: Check if the page is still accessible
   - Try refreshing or navigating to a new page

2. **Element not found**
   - Solution: Wait for the element to load
   - Use `wait_for_selector` before clicking

3. **Screenshot failures**
   - Solution: Ensure page is fully loaded
   - Check browser permissions

### Debug Mode

Enable debug logging:

```bash
export DEBUG=1
python -m cesail.mcp.fastmcp_server
```

## Performance Tips

- Use headless mode for production
- Implement proper waiting strategies
- Cache page analysis results when possible
- Use efficient selectors for element targeting

## Contributing

See the main CeSail repository for contribution guidelines. The MCP server follows the same development practices as the rest of the project.
