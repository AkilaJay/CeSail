

// Replace getPlaywrightStyleSelector with getFastRobustSelector in the code
import { convertPlaywrightSelectorToCSS } from './utility-functions';
import { selectorCache } from './cache-manager';

function getShortestUniquePath(el) {
    const parts = [];
  
    while (el && el.nodeType === 1 && el.tagName.toLowerCase() !== 'html') {
      const tag = el.tagName.toLowerCase();
      const parent = el.parentNode;
  
      if (parent) {
        const siblings = Array.from(parent.children).filter(e => e.tagName === el.tagName);
        const index = siblings.indexOf(el) + 1;
        parts.unshift(`${tag}:nth-of-type(${index})`);
      } else {
        parts.unshift(tag);
      }
  
      el = parent;
    }
  
    return parts.join(' > ');
}

function getFastRobustSelector(el) {
    if (!(el instanceof Element)) return null;
    if (selectorCache.has(el)) return selectorCache.get(el);
  
    const selectorStartTime = performance.now();
    const selectorTimings = {};
  
    // 1) ID
    const idStart = performance.now();
    if (el.id) {
      const sel = `#${CSS.escape(el.id)}`;
      if (document.querySelectorAll(sel).length === 1) {
        selectorCache.set(el, sel);
        selectorTimings.id = performance.now() - idStart;
        return sel;
      }
    }
    selectorTimings.id = performance.now() - idStart;
  
    // 2) Custom test attributes
    const testAttrsStart = performance.now();
    const testAttrs = ['data-testid','data-test-id','data-cy','data-qa'];
    for (let attr of testAttrs) {
      const v = el.getAttribute(attr);
      if (v) {
        const sel = `[${attr}="${CSS.escape(v)}"]`;
        if (document.querySelectorAll(sel).length === 1) {
          selectorCache.set(el, sel);
          selectorTimings.testAttrs = performance.now() - testAttrsStart;
          return sel;
        }
      }
    }
    selectorTimings.testAttrs = performance.now() - testAttrsStart;
  
    // 4) ARIA role + name (only if aria-label exists)
    const ariaStart = performance.now();
    const role = el.getAttribute('role');
    const aria = el.getAttribute('aria-label');
    if (role && aria) {
      // Playwright‐style locator
      const safe = aria.replace(/(["\\])/g, '\\$1');
      const sel = `role=${role}[name="${safe}"]`;
      const sel2 = convertPlaywrightSelectorToCSS(sel);
      if (document.querySelectorAll(sel2).length === 1) {
        selectorCache.set(el, sel);
        selectorTimings.aria = performance.now() - ariaStart;
        return sel;
      }
    }
    selectorTimings.aria = performance.now() - ariaStart;
  
    // 5) Tag + unique class among siblings
    const classStart = performance.now();
    const tag = el.tagName.toLowerCase();
    for (let cls of el.classList) {
      // Check if this class is unique in the entire document
      const allElementsWithClass = document.querySelectorAll(`.${CSS.escape(cls)}`);
      if (allElementsWithClass.length === 1) {
        const sel = `${tag}.${CSS.escape(cls)}`;
        selectorCache.set(el, sel);
        selectorTimings.class = performance.now() - classStart;
        return sel;
      }
    }
    selectorTimings.class = performance.now() - classStart;
  
    // 6) Fallback: shortest unique CSS path (heaviest)
    const fallbackStart = performance.now();
    const sel = getShortestUniquePath(el);
    selectorCache.set(el, sel);
    selectorTimings.fallback = performance.now() - fallbackStart;
    
    const totalSelectorTime = performance.now() - selectorStartTime;
    
    // Store timing data for summary
    if (!window.selectorTimings) {
      window.selectorTimings = {
        id: [],
        testAttrs: [],
        aria: [],
        class: [],
        fallback: [],
        total: []
      };
    }
    
    window.selectorTimings.id.push(selectorTimings.id);
    window.selectorTimings.testAttrs.push(selectorTimings.testAttrs);
    window.selectorTimings.aria.push(selectorTimings.aria);
    window.selectorTimings.class.push(selectorTimings.class);
    window.selectorTimings.fallback.push(selectorTimings.fallback);
    window.selectorTimings.total.push(totalSelectorTime);
    
    return sel;
}

export function getPlaywrightStyleSelector(element) {
    return getFastRobustSelector(element);
  }
