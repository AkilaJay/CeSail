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
