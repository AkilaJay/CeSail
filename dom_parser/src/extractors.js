// Cache for computed styles to avoid repeated calculations
let styleCache = new WeakMap();

// Pre-compile regex patterns
const INTERACTIVE_TAGS = new Set(['a', 'button', 'input', 'select', 'textarea', 'video', 'audio']);
const INTERACTIVE_ROLES = new Set(['button', 'link', 'checkbox', 'radio', 'textbox', 'combobox', 'listbox', 'menuitem', 'tab', 'switch', 'slider']);
const SENSITIVE_ATTRS = new Set(['password', 'credit-card', 'ssn', 'secret', 'token', 'key', 'auth']);
const SENSITIVE_CLASSES = new Set(['password', 'secret', 'private', 'sensitive', 'auth', 'token', 'key']);

// Batch style reading for better performance
function getComputedStyles(element) {
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
function isVisible(element) {
    if (!element || !element.getBoundingClientRect) return false;
    
    const rect = element.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return false;
    
    const styles = getComputedStyles(element);
    if (styles.display === 'none' || styles.visibility === 'hidden' || styles.opacity === 0) return false;
    
    // Check if element is in viewport
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    
    return !(rect.bottom < 0 || rect.top > viewportHeight || rect.right < 0 || rect.left > viewportWidth);
}

// Optimized element type detection
function getElementType(element) {
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
        default: return 'OTHER';
    }
}

// Optimized sensitivity check
function isSensitive(element) {
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

// Optimized interactivity check
function isInteractive(element) {
    const tag = element.tagName.toLowerCase();
    const role = element.getAttribute('role');
    
    if (INTERACTIVE_TAGS.has(tag)) return true;
    if (role && INTERACTIVE_ROLES.has(role.toLowerCase())) return true;
    
    return element.onclick != null || 
           element.getAttribute('onclick') != null ||
           element.getAttribute('tabindex') != null;
}

// Batch process attributes
function getAttributes(element) {
    const attrs = {};
    const attributes = element.attributes;
    for (let i = 0; i < attributes.length; i++) {
        const attr = attributes[i];
        attrs[attr.name] = attr.value;
    }
    return attrs;
}

// Main extraction function with optimizations
function extractElements() {
    // Clear caches before starting
    styleCache = new WeakMap();
    visibilityCache = new WeakMap();
    
    // Initialize result object
    const result = {
        meta: extractMetaData(),
        outline: extractDocumentOutline(),
        text: extractTextContent(),
        forms: extractForms(),
        media: extractMedia(),
        links: extractLinks(),
        structuredData: extractStructuredData(),
        dynamic: extractDynamicState(),
        actions: [], // Will be populated with interactive elements
        layout: extractLayoutInfo(),
        pagination: extractPaginationInfo()
    };

    // Process all elements and collect actions
    const processElement = (element) => {
        if (!element || !element.tagName) return null;
        
        // Skip invisible elements early
        if (!isVisible(element)) return null;
        
        const tag = element.tagName.toLowerCase();
        const rect = element.getBoundingClientRect();
        
        // Batch DOM reads
        const attributes = {};
        for (const attr of element.attributes) {
            attributes[attr.name] = attr.value;
        }
        
        const text = element.textContent?.trim() || '';
        const children = Array.from(element.children).map(processElement).filter(Boolean);
        
        // Check if element is interactive
        const interactive = isInteractive(element);
        const elementType = getElementType(element);
        const sensitive = isSensitive(element);
        
        const elementData = {
            tag,
            attributes,
            text,
            children,
            rect: {
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height
            },
            interactive,
            type: elementType,
            sensitive,
            role: element.getAttribute('role'),
            aria: {
                label: element.getAttribute('aria-label'),
                describedby: element.getAttribute('aria-describedby'),
                labelledby: element.getAttribute('aria-labelledby')
            },
            computedStyle: {
                display: window.getComputedStyle(element).display,
                visibility: window.getComputedStyle(element).visibility,
                zIndex: window.getComputedStyle(element).zIndex
            }
        };

        // If element is interactive, add to actions
        if (interactive) {
            result.actions.push(elementData);
        }
        
        return elementData;
    };

    // Process the entire document
    result.elements = processElement(document.documentElement);
    
    return result;
}

function extractMetaData() {
    return {
        url: window.location.href,
        canonical: document.querySelector('link[rel="canonical"]')?.href,
        title: document.title,
        meta: {
            description: document.querySelector('meta[name="description"]')?.content,
            keywords: document.querySelector('meta[name="keywords"]')?.content,
            viewport: document.querySelector('meta[name="viewport"]')?.content,
            og: {
                title: document.querySelector('meta[property="og:title"]')?.content,
                description: document.querySelector('meta[property="og:description"]')?.content,
                image: document.querySelector('meta[property="og:image"]')?.content
            }
        },
        status: document.readyState
    };
}

function extractDocumentOutline() {
    const outline = [];
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    headings.forEach(heading => {
        outline.push({
            level: parseInt(heading.tagName[1]),
            text: heading.textContent.trim(),
            id: heading.id
        });
    });
    return outline;
}

function extractTextContent() {
    const textBlocks = [];
    const paragraphs = document.querySelectorAll('p, blockquote, pre');
    paragraphs.forEach(p => {
        if (isVisible(p)) {
            textBlocks.push({
                type: p.tagName.toLowerCase(),
                text: p.textContent.trim(),
                id: p.id
            });
        }
    });
    return textBlocks;
}

function extractForms() {
    const forms = [];
    document.querySelectorAll('form').forEach(form => {
        const fields = [];
        form.querySelectorAll('input, select, textarea').forEach(field => {
            fields.push({
                type: field.type || field.tagName.toLowerCase(),
                name: field.name,
                id: field.id,
                placeholder: field.placeholder,
                value: field.value,
                required: field.required,
                pattern: field.pattern,
                min: field.min,
                max: field.max,
                options: field.tagName === 'SELECT' ? 
                    Array.from(field.options).map(opt => ({
                        value: opt.value,
                        text: opt.text
                    })) : undefined
            });
        });
        
        forms.push({
            id: form.id,
            action: form.action,
            method: form.method,
            fields
        });
    });
    return forms;
}

function extractMedia() {
    const media = [];
    
    // Images
    document.querySelectorAll('img, picture').forEach(img => {
        media.push({
            type: 'image',
            src: img.src,
            alt: img.alt,
            width: img.width,
            height: img.height,
            loading: img.loading
        });
    });
    
    // Video/Audio
    document.querySelectorAll('video, audio').forEach(mediaEl => {
        media.push({
            type: mediaEl.tagName.toLowerCase(),
            src: mediaEl.src,
            controls: mediaEl.controls,
            autoplay: mediaEl.autoplay,
            loop: mediaEl.loop,
            muted: mediaEl.muted
        });
    });
    
    return media;
}

function extractLinks() {
    const links = [];
    document.querySelectorAll('a').forEach(link => {
        if (isVisible(link)) {
            links.push({
                href: link.href,
                text: link.textContent.trim(),
                target: link.target,
                rel: link.rel
            });
        }
    });
    return links;
}

function extractStructuredData() {
    const data = [];
    document.querySelectorAll('script[type="application/ld+json"]').forEach(script => {
        try {
            data.push(JSON.parse(script.textContent));
        } catch (e) {
            console.warn('Failed to parse JSON-LD:', e);
        }
    });
    return data;
}

function extractDynamicState() {
    return {
        modals: Array.from(document.querySelectorAll('[role="dialog"], [role="alertdialog"]'))
            .filter(isVisible)
            .map(modal => ({
                id: modal.id,
                role: modal.getAttribute('role'),
                text: modal.textContent.trim()
            })),
        notifications: Array.from(document.querySelectorAll('[role="alert"], [role="status"]'))
            .filter(isVisible)
            .map(notif => ({
                id: notif.id,
                role: notif.getAttribute('role'),
                text: notif.textContent.trim()
            })),
        loading: Array.from(document.querySelectorAll('[role="progressbar"], .loading, .spinner'))
            .filter(isVisible)
            .map(loader => ({
                id: loader.id,
                type: loader.getAttribute('role') || 'spinner'
            }))
    };
}

function extractLayoutInfo() {
    const layout = [];
    const sections = document.querySelectorAll('header, nav, main, footer, section, article, aside');
    sections.forEach(section => {
        if (isVisible(section)) {
            const rect = section.getBoundingClientRect();
            layout.push({
                type: section.tagName.toLowerCase(),
                id: section.id,
                rect: {
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height
                },
                zIndex: window.getComputedStyle(section).zIndex
            });
        }
    });
    return layout;
}

function extractPaginationInfo() {
    const pagination = {
        next: document.querySelector('a[rel="next"]')?.href,
        prev: document.querySelector('a[rel="prev"]')?.href,
        pages: Array.from(document.querySelectorAll('.pagination a, [role="navigation"] a'))
            .filter(link => /^\d+$/.test(link.textContent.trim()))
            .map(link => ({
                number: parseInt(link.textContent.trim()),
                href: link.href
            }))
    };
    return pagination;
}

// Export the function
window.extractElements = extractElements; 