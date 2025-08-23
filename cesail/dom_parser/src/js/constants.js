// Constants and configuration for DOM extractors

// Pre-compile regex patterns
export const INTERACTIVE_TAGS = new Set([
    'a', 'button', 'input', 'select', 'textarea', 'video', 'audio',
    'summary', 'details', 'menu', 'menuitem'
]);

export const INTERACTIVE_ROLES = new Set([
    'button', 'link', 'checkbox', 'radio', 'textbox', 'combobox', 
    'listbox', 'menuitem', 'tab', 'switch', 'slider', 'option',
    'menuitemcheckbox', 'menuitemradio', 'treeitem'
]);

export const SENSITIVE_ATTRS = new Set(['password', 'credit-card', 'ssn', 'secret', 'token', 'key', 'auth']);
export const SENSITIVE_CLASSES = new Set(['password', 'secret', 'private', 'sensitive', 'auth', 'token', 'key']);

// Attribute weights for scoring elements
export const ATTRIBUTE_WEIGHTS = {
    // 1) Unique locators (highest)
    id: 10,
    'data-testid': 9,
    'data-test-id': 9,
    'data-cid': 9,
    jsname: 8,
    jsaction: 8,

    // 2) ARIA & roles
    role: 9,
    'aria-label': 8,
    'aria-labelledby': 7,

    // 3) Navigation / resource URLs
    href: 8,
    src: 7,
    action: 7,

    // 4) Semantic behavior hooks
    onclick: 7,
    placeholder: 5,

    // 5) Accessibility semantics
    alt: 6,
    title: 5,

    // 6) Form state
    disabled: -5,   // less important if disabled
    checked: 4,
    selected: 4,
    hidden: -10,  // not visible → very low importance
    'aria-hidden': -10,  // ditto

    // 7) Styling / generic hooks
    class: 5,
    'data-action': 6,
    'data-toggle': 6,
    isContentEditable: 4,
};

// ARIA-specific weights for accessibility scoring
export const ARIA_WEIGHTS = {
    'aria-label': 9,   // explicit accessible name
    'aria-labelledby': 8,   // references one or more other elements' text
    'aria-describedby': 6    // supplemental description, less primary
};

// Style weights for scoring elements
export const STYLE_WEIGHTS = {
    // display
    display: {
        none: -20,   // not rendered
        hidden: -20,   // equivalent to none
        'inline': 2,   // small but visible
        'inline-block': 3,
        'block': 4,
        'flex': 5,
        'grid': 5,
        'table': 3,
        'table-row': 2,
        'table-cell': 2,
        // any other displays you care about  
    },

    // visibility
    visibility: {
        hidden: -20,   // present in flow but invisible
        collapse: -10,   // table rows/columns
        visible: 5     // fully visible
    },

    // zIndex: raw numeric value scaled/logged
    zIndex: {
        weightFactor: 0.1 // multiply zIndex by this (e.g. zIndex 50 → +5)
    }
};

// Instead, find and process all interactive elements directly
export const INTERACTIVE_SELECTORS = [
    // Interactive tags
    'button', 'a[href]', 'input', 'select', 'textarea', 'label', 'summary', 'details',
    
    // ARIA roles
    '[role="button"]', '[role="link"]', '[role="menuitem"]', '[role="checkbox"]', 
    '[role="radio"]', '[role="switch"]', '[role="tab"]', '[role="slider"]', 
    '[role="combobox"]', '[role="textbox"]', '[role="search"]', '[role="option"]',
    '[role="menuitemcheckbox"]', '[role="menuitemradio"]', '[role="treeitem"]',
    
    // Tabindex (including implicit tabindex)
    '[tabindex]',
    
    // Click handlers
    '[onclick]',
    
    // Interactive attributes
    '[href]', '[src]', '[action]', '[data-action]', '[data-toggle]',
    
    // Contenteditable
    '[contenteditable]',
    
    // Form controls
    'fieldset', 'legend',
    
    // Additional interactive elements
    'video', 'audio', 'canvas', 'svg', 'iframe', 'img[usemap]', 'area',
    'object', 'embed', 'applet', 'marquee', 'blink'
];
