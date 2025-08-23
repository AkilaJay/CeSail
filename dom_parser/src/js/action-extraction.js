import { INTERACTIVE_SELECTORS } from './constants';
import { isVisible, isInteractive, getElementType, isSensitive } from './utility-functions';
import { getPlaywrightStyleSelector } from './selector-extraction';

// Function to extract metadata from a container
function extractContainerMetadata(container) {
    const metadata = {
        title: null,
        price: null,
        image: null,
        sku: null,
        description: null
    };
    
    // Find title/name
    const titleSelectors = [
        'h1, h2, h3, [class*="title"], [class*="name"], [itemprop="name"]',
        '[data-product-title], [data-item-title]',
        '.product-title, .item-title, .card-title'
    ];
    
    for (const selector of titleSelectors) {
        const titleEl = container.querySelector(selector);
        if (titleEl && titleEl.textContent.trim()) {
            metadata.title = titleEl.textContent.trim();
            break;
        }
    }
    
    // Find price
    const priceSelectors = [
        '[class*="price"], [itemprop="price"], .amount, .cost, .value',
        '[data-price], [data-cost]',
        '.product-price, .item-price, .card-price'
    ];
    
    for (const selector of priceSelectors) {
        const priceEl = container.querySelector(selector);
        if (priceEl && priceEl.textContent.trim()) {
            metadata.price = priceEl.textContent.trim();
            break;
        }
    }
    
    // Find image
    const img = container.querySelector('img');
    if (img) {
        metadata.image = {
            src: img.src,
            alt: img.alt
        };
    }
    
    // Find SKU
    const skuSelectors = [
        '[data-sku], [data-product-id], [data-item-id]',
        '[itemprop="sku"]',
        '.product-sku, .item-sku'
    ];
    
    for (const selector of skuSelectors) {
        const skuEl = container.querySelector(selector);
        if (skuEl) {
            metadata.sku = skuEl.textContent.trim() || skuEl.getAttribute('data-sku') || 
                          skuEl.getAttribute('data-product-id') || skuEl.getAttribute('data-item-id');
            break;
        }
    }
    
    // Find description
    const descSelectors = [
        '[itemprop="description"]',
        '[data-description]',
        '.product-description, .item-description'
    ];
    
    for (const selector of descSelectors) {
        const descEl = container.querySelector(selector);
        if (descEl && descEl.textContent.trim()) {
            metadata.description = descEl.textContent.trim();
            break;
        }
    }
    
    return metadata;
}

export function extractActions() {

    const processElement = (element) => {
        if (!element || !element.tagName) return null;

        // Skip invisible elements early
        if (!isVisible(element)) return null;

        const tag = element.tagName.toLowerCase();
        const rect = element.getBoundingClientRect();
        
        // Batch DOM reads
        const attributesStart = performance.now();
        const attributes = {};
        for (const attr of element.attributes) {
            attributes[attr.name] = attr.value;
        }

        const text = element.textContent?.trim() || '';

        // Check if element is interactive
        const interactive = isInteractive(element);
        const elementType = getElementType(element);
        const sensitive = isSensitive(element);

        // Generate Playwright-style selector
        let selector = null;
        try {
            selector = getPlaywrightStyleSelector(element);
        } catch (e) {
            selector = null;
        }

        const elementData = {
            tag,
            attributes,
            text,
            rect: {
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height,
                top: rect.top,
                left: rect.left,
                bottom: rect.bottom,
                right: rect.right
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
            },
            selector,
            object: element
        };
        
        return elementData;
    };

    const foundElements = new Map();
    for (const selector of INTERACTIVE_SELECTORS) {
        const elements = document.querySelectorAll(selector);
        for (const element of elements) {
            if (isVisible(element) && isInteractive(element)) {
                const processed = processElement(element);
                if (processed) {
                    foundElements.set(element, processed);
                }
            }
        }
    }

    return foundElements;
}

export function extractMetaData() {
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

export function extractDocumentOutline() {
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

export function extractTextContent() {
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

export function extractForms() {
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

export function extractMedia() {
    const media = [];
    
    // Images
    document.querySelectorAll('img, picture').forEach(img => {
        let rawSrc = img.src || '';
        let src = rawSrc.length > 200
          ? rawSrc.slice(0, 200)  // take only the first 300 chars
          : rawSrc;
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
        let rawSrc = mediaEl.src || '';
        let src = rawSrc.length > 200
          ? rawSrc.slice(0, 200)  // take only the first 300 chars
          : rawSrc;
        media.push({
            type: mediaEl.tagName.toLowerCase(),
            src: src,
            controls: mediaEl.controls,
            autoplay: mediaEl.autoplay,
            loop: mediaEl.loop,
            muted: mediaEl.muted
        });
    });
    
    return media;
}

export function extractLinks() {
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

export function extractStructuredData() {
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

export function extractDynamicState() {
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

export function extractLayoutInfo() {
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

export function extractPaginationInfo() {
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