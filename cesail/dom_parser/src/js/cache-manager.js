// Cache management for DOM extractors

// Cache for computed styles to avoid repeated calculations
export let styleCache = new Map();

// Add global Set for top-level elements
export let topLevelElementsCache = new Map();

// Add selector cache
export let selectorMap = new Map();

// Add selector cache
export let selectorCache = new WeakMap();

export let nextSelectorId = 1;

export const clearStyleCache = () => {
    styleCache.clear();
}

export function clearTopLevelElementsCache() {
    topLevelElementsCache.clear();
}

export function clearSelectorMap() {
    selectorMap.clear();
    nextSelectorId = 1;
}

export function clearSelectorCache() {
    selectorCache = new WeakMap();
}

export function incrementSelectorId() {
    nextSelectorId++;
    return nextSelectorId;
}