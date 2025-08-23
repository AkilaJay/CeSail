# DOM Parser JavaScript Layer

Core DOM parsing engine that transforms raw HTML into structured, agent-friendly data.

## Overview

The JavaScript layer is the heart of CeSail's DOM parsing capabilities. It runs directly in the browser context and provides comprehensive element extraction, analysis, and transformation functionality.

## Key Components

### Core Files

- **`index.js`**: Main entry point and public API
- **`action-extraction.js`**: Extracts actionable elements and metadata
- **`filter-elements.js`**: Filters and groups elements by importance
- **`scoring.js`**: Scores elements based on visibility and interactivity
- **`selector-extraction.js`**: Generates reliable CSS selectors
- **`visualizer.js`**: Visual debugging and element highlighting
- **`cache-manager.js`**: Performance optimization and caching
- **`utility-functions.js`**: Common utility functions
- **`constants.js`**: Configuration constants and weights
- **`perf.js`**: Performance monitoring and profiling

## Features

- **Element Extraction**: Identifies and categorizes interactive elements (buttons, forms, links)
- **Semantic Analysis**: Understands element purpose and context
- **Action Mapping**: Maps elements to executable actions (click, type, navigate)
- **Text Scoring**: Prioritizes important text content for agents
- **Selector Generation**: Creates reliable CSS selectors for element targeting
- **Performance Optimization**: Caching and monitoring for speed
- **ARIA Support**: Accessibility attribute analysis
- **Visual Context**: Combines DOM data with visual information
- **Processing Pipeline**: Multi-stage element processing and filtering

## Data Transformation

The JavaScript layer transforms raw HTML into structured, agent-friendly JSON:

```javascript
// Raw HTML input
<button class="btn-primary" onclick="submit()">Submit Form</button>
<input type="text" placeholder="Enter email" id="email" />

// CeSail transforms to agent-friendly JSON
{
  "type": "BUTTON",
  "selector": "button.btn-primary",
  "text": "Submit Form",
  "action": "CLICK",
  "importance": 0.9,
  "context": "form submission",
  "metadata": {
    "aria-label": null,
    "disabled": false,
    "visible": true
  }
}
```

## Usage

This layer is automatically injected into web pages by the Python DOM Parser and provides APIs for:

- Element extraction and analysis
- Action mapping and execution
- Visual debugging and highlighting
- Performance monitoring
- Caching and optimization

## Architecture

The JavaScript layer operates as a browser-injected script that:

1. **Analyzes** the current DOM structure
2. **Extracts** actionable elements and metadata
3. **Scores** elements by importance and visibility
4. **Filters** and groups elements appropriately
5. **Generates** reliable selectors for targeting
6. **Provides** APIs for the Python layer to consume

## Performance

- Caching system for repeated operations
- Performance monitoring and profiling
- Optimized element traversal algorithms
- Memory-efficient data structures

## Build Process

The JavaScript layer must be built before it can be used by the Python DOM Parser.

### Building the Bundle

```bash
cd dom_parser/
npm install  # Installs Rollup and build dependencies
npm run build
```

This creates the bundled JavaScript file at `dom_parser/dist/dom-parser.js` which contains:
- All DOM parsing functions from `src/js/`
- Element extraction and analysis logic
- Selector generation and mapping
- Performance monitoring and caching

### Integration with Python Layer

The Python `DOMParser` automatically injects the built JavaScript bundle into every browser page:

```python
# The bundle is automatically loaded from:
bundle_path = Path(__file__).parent.parent / "dist" / "dom-parser.js"

# And injected as an init script:
await self.context.add_init_script(path=str(self.bundle_path))
```

### Build Configuration

The JavaScript is built using **Rollup** with the following outputs:
- **IIFE Bundle** (`dist/dom-parser.js`) - Main bundle for browser injection
- **ES Module** (`dist/dom-parser.esm.js`) - For modern module systems
- **UMD Bundle** (`dist/dom-parser.umd.js`) - For Node.js compatibility

### Development Workflow

```bash
# Watch mode for development
npm run dev

# Clean and rebuild
npm run clean && npm run build

# Simple build (alternative)
npm run build:simple
```

**Note:** Always rebuild the JavaScript bundle after making changes to files in `src/js/` before testing the Python layer.
