import { styleCache } from './cache-manager';
import { INTERACTIVE_TAGS, INTERACTIVE_ROLES, SENSITIVE_ATTRS, SENSITIVE_CLASSES } from './constants';


export function isInteractive(element) {
    const tag = element.tagName.toLowerCase();
    const role = element.getAttribute('role');

    if (tag === 'form') {
        return false;
    }
    
    // Check for interactive tags and roles
    if (INTERACTIVE_TAGS.has(tag)) return true;
    if (role && INTERACTIVE_ROLES.has(role.toLowerCase())) return true;
    
    // Check for tabindex (including implicit tabindex)
    if (element.hasAttribute('tabindex') || element.tabIndex >= 0) return true;
    
    // Check for click handlers
    if (element.onclick != null || element.getAttribute('onclick') != null) return true;
    
    // Check for common interactive attributes
    const interactiveAttrs = ['href', 'src', 'action', 'data-action', 'data-toggle'];
    if (interactiveAttrs.some(attr => element.hasAttribute(attr))) return true;
    
    // Check for form controls
    // if (element.form || element.tagName === 'LABEL') return true;
    
    // Check for contenteditable
    if (element.isContentEditable) return true;
    
    return false;
}

// Batch style reading for better performance
export function getComputedStyles(element) {
    if (styleCache.has(element)) {
        return styleCache.get(element);
    }
    
    const styles = window.getComputedStyle(element);
    const styleInfo = {
        display: styles.display,
        visibility: styles.visibility,
        opacity: parseFloat(styles.opacity),
        position: styles.position,
        zIndex: parseInt(styles.zIndex) || 0
    };
    
    styleCache.set(element, styleInfo);
    return styleInfo;
}

// Optimized visibility check with caching and early returns
export function isVisible(element) {
    const visibilityStartTime = performance.now();
    
    if (!element || !element.getBoundingClientRect) {
        // Store timing data for early return
        if (!window.visibilityTimings) {
            window.visibilityTimings = {
                earlyReturn: [],
                getBoundingClientRect: [],
                getComputedStyles: [],
                viewportCheck: [],
                total: []
            };
        }
        window.visibilityTimings.earlyReturn.push(performance.now() - visibilityStartTime);
        window.visibilityTimings.total.push(performance.now() - visibilityStartTime);
        return false;
    }
    
    // Skip visibility check for the html element
    if (element.tagName.toLowerCase() === 'html') {
        if (!window.visibilityTimings) {
            window.visibilityTimings = {
                earlyReturn: [],
                getBoundingClientRect: [],
                getComputedStyles: [],
                viewportCheck: [],
                total: []
            };
        }
        window.visibilityTimings.earlyReturn.push(performance.now() - visibilityStartTime);
        window.visibilityTimings.total.push(performance.now() - visibilityStartTime);
        return true;
    }
    
    const rectStart = performance.now();
    const rect = element.getBoundingClientRect();
    const rectTime = performance.now() - rectStart;
    
    const stylesStart = performance.now();
    const styles = getComputedStyles(element);
    const stylesTime = performance.now() - stylesStart;
    
    if (styles.display === 'none' || styles.visibility === 'hidden' || styles.opacity === 0) {
        // Store timing data for early return
        if (!window.visibilityTimings) {
            window.visibilityTimings = {
                earlyReturn: [],
                getBoundingClientRect: [],
                getComputedStyles: [],
                viewportCheck: [],
                total: []
            };
        }
        window.visibilityTimings.getBoundingClientRect.push(rectTime);
        window.visibilityTimings.getComputedStyles.push(stylesTime);
        window.visibilityTimings.earlyReturn.push(performance.now() - visibilityStartTime);
        window.visibilityTimings.total.push(performance.now() - visibilityStartTime);
        return false;
    }
    
    const viewportStart = performance.now();
    // Check if element is in viewport
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    
    // Relax viewport check to include elements that might be scrolled into view
    const result = !(rect.bottom < -100 || rect.top > viewportHeight + 100 || 
             rect.right < -100 || rect.left > viewportWidth + 100);
    const viewportTime = performance.now() - viewportStart;
    
    // Store timing data
    if (!window.visibilityTimings) {
        window.visibilityTimings = {
            earlyReturn: [],
            getBoundingClientRect: [],
            getComputedStyles: [],
            viewportCheck: [],
            total: []
        };
    }
    
    window.visibilityTimings.getBoundingClientRect.push(rectTime);
    window.visibilityTimings.getComputedStyles.push(stylesTime);
    window.visibilityTimings.viewportCheck.push(viewportTime);
    window.visibilityTimings.total.push(performance.now() - visibilityStartTime);
    
    return result;
}

// Optimized element type detection
export function getElementType(element) {
    const tag = element.tagName.toLowerCase();
    const role = element.getAttribute('role');
    const type = element.getAttribute('type');
    
    // Check role first (ARIA roles take precedence)
    if (role) {
        switch (role.toLowerCase()) {
            case 'button': return 'BUTTON';
            case 'link': return 'LINK';
            case 'checkbox': return 'CHECKBOX';
            case 'radio': return 'RADIO';
            case 'switch': return 'TOGGLE';
            case 'slider': return 'SLIDER';
            case 'textbox': return 'INPUT';
            case 'combobox': return 'SELECT';
            case 'tab': return 'TAB';
            case 'menuitem': return 'BUTTON';
            case 'listbox': return 'SELECT';
            case 'search': return 'FORM';
            case 'option': return 'BUTTON';
            case 'menuitemcheckbox': return 'CHECKBOX';
            case 'menuitemradio': return 'RADIO';
            case 'treeitem': return 'BUTTON';
        }
    }
    
    // Then check tag and type
    switch (tag) {
        case 'a': return 'LINK';
        case 'button': return 'BUTTON';
        case 'input':
            switch (type?.toLowerCase()) {
                case 'checkbox': return 'CHECKBOX';
                case 'radio': return 'RADIO';
                case 'range': return 'SLIDER';
                case 'date': return 'DATEPICKER';
                case 'file': return 'FILE_INPUT';
                case 'submit': return 'BUTTON';
                case 'reset': return 'BUTTON';
                case 'image': return 'BUTTON';
                case 'search': return 'INPUT';
                default: return 'INPUT';
            }
        case 'textarea': return 'TEXTAREA';
        case 'select': return 'SELECT';
        case 'video': return 'VIDEO';
        case 'audio': return 'AUDIO';
        case 'table': return 'TABLE';
        case 'tr': return 'TABLE_ROW';
        case 'td':
        case 'th': return 'TABLE_CELL';
        case 'form': return 'FORM';
        case 'svg': return 'SVG';
        case 'canvas': return 'CANVAS';
        case 'iframe': return 'IFRAME';
        case 'img': return 'IMAGE';
        case 'label': return 'LABEL';
        case 'summary': return 'SUMMARY';
        case 'details': return 'DETAILS';
        case 'menu': return 'MENU';
        case 'menuitem': return 'MENUITEM';
        default: 
            // Check if element has interactive attributes
            if (element.hasAttribute('href') || element.hasAttribute('src') || 
                element.hasAttribute('action') || element.hasAttribute('data-action') || 
                element.hasAttribute('data-toggle') || element.isContentEditable) {
                return 'BUTTON';
            }
            return 'OTHER';
    }
}

// Optimized sensitivity check
export function isSensitive(element) {
    const attrs = element.attributes;
    for (let i = 0; i < attrs.length; i++) {
        const attr = attrs[i].name.toLowerCase();
        const value = attrs[i].value.toLowerCase();
        
        if (SENSITIVE_ATTRS.has(attr) || SENSITIVE_ATTRS.has(value)) {
            return true;
        }
    }
    
    // Handle both string and DOMTokenList cases for className
    let classes;
    if (typeof element.className === 'string') {
        classes = element.className.toLowerCase().split(' ');
    } else if (element.classList) {
        classes = Array.from(element.classList).map(c => c.toLowerCase());
    } else {
        classes = [];
    }
    
    return classes.some(cls => SENSITIVE_CLASSES.has(cls));
}

export function convertPlaywrightSelectorToCSS(selector) {
    if (!selector || typeof selector !== 'string') {
        return null;
    }

    try {
        // Handle role-based selectors
        if (selector.startsWith('role=')) {
            const match = selector.match(/role=([^\[]+)(?:\[name="([^"]+)"\])?/);
            if (match) {
                const role = match[1];
                const name = match[2];
                if (name) {
                    // Try multiple ARIA attribute combinations for the name
                    return `[role="${role}"][aria-label="${name}"], [role="${role}"][title="${name}"], [role="${role}"][alt="${name}"]`;
                }
                return `[role="${role}"]`;
            }
        }

        // Handle other Playwright selectors
        if (selector.includes('[') && selector.includes(']')) {
            // Convert Playwright attribute syntax to CSS
            return selector
                .replace(/\[([^\]]+)\]/g, (match, attr) => {
                    if (attr.includes('=')) {
                        const [name, value] = attr.split('=');
                        return `[${name}="${value.replace(/"/g, '')}"]`;
                    }
                    return match;
                });
        }

        return selector;
    } catch (e) {
        console.warn('Error converting selector:', selector, e);
        return null;
    }
}

// Batch process attributes
export function getAttributes(element) {
    const attrs = {};
    const attributes = element.attributes;
    for (let i = 0; i < attributes.length; i++) {
        const attr = attributes[i];
        attrs[attr.name] = attr.value;
    }
    return attrs;
}