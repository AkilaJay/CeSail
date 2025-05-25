# DOM Parser

A Python library for parsing and analyzing web pages to generate action graphs. This library helps you understand the structure of web pages and identify possible interactions.

## Features

- Parse web pages and extract their structure
- Identify interactive elements (buttons, links, forms, etc.)
- Generate possible actions for each interactive element
- Handle sensitive information (passwords, credit cards, etc.)
- Async/await support for better performance
- Type hints for better IDE support

## Installation

```bash
pip install dom-parser
```

## Quick Start

```python
import asyncio
from dom_parser.src.graph_generator import GraphGenerator

async def main():
    # Create a graph generator
    async with GraphGenerator(headless=True) as generator:
        # Generate an action graph for a URL
        action_graph = await generator.generate_graph("https://example.com")
        
        # Access the results
        print(f"Found {len(action_graph.nodes)} elements")
        print(f"Generated {len(action_graph.edges)} possible actions")

asyncio.run(main())
```

## Usage

### Basic Usage

```python
from dom_parser.src.graph_generator import GraphGenerator

async def analyze_page(url: str):
    async with GraphGenerator() as generator:
        # Generate the action graph
        action_graph = await generator.generate_graph(url)
        
        # Access elements
        for element in action_graph.nodes:
            if element.is_interactive:
                print(f"Found interactive element: {element.tag}")
        
        # Access actions
        for action in action_graph.edges:
            print(f"Possible action: {action.description}")

```

### Handling Sensitive Information

The library automatically identifies and handles sensitive information:

- Passwords
- Email addresses
- Credit card numbers
- Phone numbers
- Social security numbers

Sensitive elements are marked with `is_sensitive=True` and their actions are modified to protect the information.

## API Reference

### GraphGenerator

The main class for generating action graphs.

```python
generator = GraphGenerator(headless=True)
action_graph = await generator.generate_graph(url)
```

### ActionGraph

The result of analyzing a page.

```python
class ActionGraph:
    url: str
    nodes: List[ElementInfo]  # Page elements
    edges: List[Action]       # Possible actions
    metadata: Dict[str, Any]  # Additional information
```

### ElementInfo

Information about a page element.

```python
class ElementInfo:
    id: str
    type: ElementType
    tag: str
    text: Optional[str]
    attributes: Dict[str, str]
    bounding_box: BoundingBox
    is_visible: bool
    is_interactive: bool
    is_sensitive: bool
    children: List[ElementInfo]
```

### Action

A possible interaction with a page element.

```python
class Action:
    type: ActionType
    element_id: str
    description: str
    confidence: float
    value: Optional[str]
    metadata: Dict[str, Any]
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
