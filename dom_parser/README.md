# DOM Parser

A comprehensive DOM parser for extracting interactive elements and page structure from web pages.

## Features

- **Element Extraction**: Find and analyze interactive elements (buttons, links, forms, etc.)
- **Text Analysis**: Extract and score important text content
- **Selector Generation**: Generate robust CSS selectors for elements
- **Performance Monitoring**: Built-in timing and profiling capabilities
- **Modular Architecture**: Clean ES module structure for maintainability

## Installation

```bash
npm install dom-parser
```

## Usage

### ES Modules (Recommended)

```javascript
import { extractElements } from 'dom-parser';

// Extract all interactive elements from the current page
const result = await extractElements();
console.log(result.actions); // Array of interactive elements
```

### Browser (IIFE Bundle)

```html
<script src="dist/dom-parser.bundle.js"></script>
<script>
  // Now DOMParserExtract.extractElements is globally available
  DOMParserExtract.extractElements().then(result => {
    console.log(result.actions);
  });
</script>
```

### Browser (ES Module)

```html
<script type="module">
  import { extractElements } from '/dist/dom-parser.esm.js';
  
  const result = await extractElements();
  console.log(result.actions);
</script>
```

## API Reference

### Main Functions

#### `extractElements()`
Extracts all interactive elements and page metadata from the current DOM.

**Returns:** `Promise<Object>` - Object containing:
- `actions`: Array of interactive elements
- `meta`: Page metadata
- `outline`: Document structure
- `text`: Text content
- `forms`: Form information
- `media`: Media elements
- `links`: Link elements
- `importantElements`: Most important elements
- `logs`: Processing logs

#### `getTopLevelElements()`
Gets the top-level elements that contain multiple interactive elements.

**Returns:** `Array` - Array of top-level elements

#### `transformTopLevelElements(elements)`
Transforms raw elements into a structured format with scoring.

**Parameters:**
- `elements`: Array of elements to transform

**Returns:** `Array` - Transformed elements with scores

### Element Analysis

#### `isVisible(element)`
Checks if an element is visible on the page.

#### `isInteractive(element)`
Determines if an element is interactive (clickable, focusable, etc.).

#### `getElementType(element)`
Gets the type of an element (BUTTON, LINK, INPUT, etc.).

#### `getFastRobustSelector(element)`
Generates a robust CSS selector for an element.

### Text Extraction

#### `getLabelText(element)`
Extracts label text for an element from various sources.

#### `crawlDownForText(element, maxDepth)`
Crawls down the DOM tree to extract text.

#### `crawlUpForText(element, maxDepth)`
Crawls up the DOM tree to extract text.

### Scoring Functions

#### `scoreElementByAria(element)`
Scores an element based on its ARIA attributes.

#### `scoreElementByStyle(element)`
Scores an element based on its computed styles.

#### `scoreElementByAttributes(attributes)`
Scores an element based on its attributes.

#### `computeImportanceScore(element)`
Computes an overall importance score for an element.

## Development

### Project Structure

```
src/
├── index.js                 # Main entry point
└── modules/
    ├── cache-manager.js     # Caching and profiling
    ├── constants.js         # Constants and configuration
    ├── element-analysis.js  # Element analysis functions
    ├── element-scoring.js   # Element scoring functions
    ├── extraction-functions.js # Content extraction
    └── utility-functions.js # Utility and helper functions
```

### Building

```bash
# Install dependencies
npm install

# Build for production
npm run build

# Development mode with watch
npm run dev
```

### Build Outputs

- `dist/dom-parser.bundle.js` - IIFE bundle for direct browser use
- `dist/dom-parser.esm.js` - ES module bundle
- `dist/dom-parser.umd.js` - UMD bundle for Node.js compatibility

## Performance

The parser includes comprehensive performance monitoring:

- **Timing Data**: Detailed timing for each processing step
- **Profiling**: Running averages and statistics
- **Caching**: Intelligent caching of computed styles and selectors
- **Tree Shaking**: Unused code is eliminated during bundling

## Browser Compatibility

- Modern browsers with ES6+ support
- IE11+ (with polyfills)
- Node.js 14+

## License

MIT
