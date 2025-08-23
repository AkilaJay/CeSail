import { ARIA_WEIGHTS, ATTRIBUTE_WEIGHTS } from './constants';
import { getInverseElementRank } from './scoring';
import { getElementType } from './utility-functions';

function getLabelText(el) {
    if (!(el instanceof Element)) return '';
  
    const seen = new Set();
    const texts = [];
  
    // Skip hidden elements
    const isHidden = el => {
      const style = window.getComputedStyle(el);
      return (
        el.getAttribute('aria-hidden') === 'true' ||
        style.display === 'none' ||
        style.visibility === 'hidden'
      );
    };
  
    // Helper to extract visible trimmed text
    const getVisibleText = el => {
      return el.textContent?.trim() || '';
    };
  
    // Add only if not empty and not seen before
    const addText = t => {
      const text = t.trim();
      if (text && !seen.has(text)) {
        seen.add(text);
        texts.push(text);
      }
    };
  
    // 1. aria-label
    const ariaLabel = el.getAttribute('aria-label');
    if (ariaLabel) addText(ariaLabel);
  
    // 2. aria-labelledby
    const labelledBy = el.getAttribute('aria-labelledby');
    if (labelledBy) {
      labelledBy.split(/\s+/).forEach(id => {
        const ref = document.getElementById(id);
        if (ref && !isHidden(ref)) addText(getVisibleText(ref));
      });
    }
  
    // 3. alt (for <img>, <area>, etc.)
    if (el.hasAttribute('alt')) addText(el.getAttribute('alt'));
  
    // 4. placeholder (e.g., <input placeholder="Search">)
    if (el.hasAttribute('placeholder')) addText(el.getAttribute('placeholder'));
  
    // 5. title (tooltip text)
    if (el.hasAttribute('title')) addText(el.getAttribute('title'));
  
    // 6. button/input "value"
    if (el.tagName === 'INPUT' || el.tagName === 'BUTTON') {
      const type = el.getAttribute('type');
      if (type === 'submit' || type === 'reset' || type === 'button') {
        if (el.value) addText(el.value);
      }
    }
  
    // 7. Associated <label for="id">
    if (el.id) {
      const label = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
      if (label && !isHidden(label)) addText(getVisibleText(label));
    }
  
    // 8. Wrapping label (e.g. <label><input> Foo</label>)
    const wrappingLabel = el.closest('label');
    if (wrappingLabel && !isHidden(wrappingLabel)) addText(getVisibleText(wrappingLabel));
  
    // 9. <legend> inside fieldset
    const fieldset = el.closest('fieldset');
    if (fieldset) {
      const legend = fieldset.querySelector('legend');
      if (legend && !isHidden(legend)) addText(getVisibleText(legend));
    }
  
    // 10. Direct visible text content
    if (!isHidden(el)) addText(getVisibleText(el));
  
    return texts.join(' | ');
}
  
// Quickly gather label/text from descendants of an element
function getDownstreamLabelText(rootEl, options = {}) {
    const { maxNodes = 50, maxChars = 300, includeSelf = false } = options;
    if (!rootEl || !(rootEl instanceof Element)) return '';

    const texts = [];
    const seen = new Set();

    const add = (t) => {
        const v = (t || '').trim();
        if (!v) return;
        if (seen.has(v)) return;
        seen.add(v);
        texts.push(v);
    };

    try {
        let scanned = 0;
        if (includeSelf) add(getLabelText(rootEl));

        // Use TreeWalker to efficiently traverse elements
        const walker = document.createTreeWalker(rootEl, NodeFilter.SHOW_ELEMENT);
        while (walker.nextNode()) {
            const el = walker.currentNode;
            add(getLabelText(el));
            scanned++;
            if (scanned >= maxNodes) break;
            if (texts.join(' | ').length >= maxChars) break;
        }
    } catch (_) {
        // Fallback: conservative empty string
    }

    let out = texts.join(' | ');
    if (out.length > maxChars) out = out.slice(0, maxChars);
    return out;
}

// New DFS-based functionality for computing counts and aggregating text
function computeCountsAndText(root, actionableSet) {
    const infoMap = new WeakMap();

    function dfs(node) {
        if (!node || !node.children) {
            return { count: 0, text: '' };
        }
        
        let count = actionableSet.has(node) ? 1 : 0;
        let inActionableSet = false;
        if (count > 0) {
            inActionableSet = true;
        }
        // collect text only for actionable nodes (or you could collect all text)
        let text = getLabelText(node);

        let totalCount = 0;
        for (const child of node.children) {
            const { count: c2, text: t2 } = dfs(child);
            totalCount += c2;
            if (t2) text += (text ? ' ' : '') + t2;
        }

        count += totalCount;
        if (count > 1) {
            count = 1;
        }

        if (totalCount > 1) {
            infoMap.set(node, {count: 2, text, inActionableSet });
        } else {
            infoMap.set(node, {count, text, inActionableSet });
        }

        return { count, text };
    }

    dfs(root);
    return infoMap;
}

// Function to group actionable elements under their minimal containers using DFS approach
export function groupActionableElementsDFS(foundElements) {    
    // // 1) identify actionable elements
    // const actionableSet = new Map(); // element → actionData
    // for (const f of foundElements) {
    //     try {
    //         actionableSet.set(f.object, f);
    //     } catch (e) {
    //         console.warn('Error converting selector to element:', f.selector, e);
    //     }
    // }
    
    // 2) run the DFS
    const infoMap = computeCountsAndText(document.body, foundElements);


    const topLevelElementsCache = new Map();
    
    for (const [el, actionData] of foundElements) {
        let node = el;
        let elementActions = [];

        if (infoMap.get(node) && infoMap.get(node).count > 1){
            continue;
        }
        
        // climb until parent has count > 1 (so you stop at the smallest container that holds >1 action)
        while (node.parentElement && 
               infoMap.has(node.parentElement) && 
               infoMap.get(node.parentElement).count < 2) {
            // Collect action data from current node if it's in actionable set
            const nodeInfo = infoMap.get(node);
            if (nodeInfo && nodeInfo.inActionableSet) {
                elementActions.push(foundElements.get(node));
            }
            node = node.parentElement;
        }
        
        // Collect action data from the final group root if it's in actionable set
        const rootInfo = infoMap.get(node);
        if (rootInfo && rootInfo.inActionableSet) {
            elementActions.push(foundElements.get(node));
        }
        
        // // Add to topLevelElementsCache as we find group roots
        const rect = node.getBoundingClientRect();
        // const nodeKey = `${rect.top},${rect.left},${rect.width},${rect.height}`;
        
        if (!topLevelElementsCache.has(node)) {
            const tmpElement = {
                top: rect.top,
                left: rect.left,
                width: rect.width,
                height: rect.height,
                actions: elementActions || []
            }
            topLevelElementsCache.set(node, tmpElement);
        }
    }

    return topLevelElementsCache;
}

// Function to check if an element is truly clickable (not occluded)
function isTrulyClickable(el) {
    const rect = el.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return false;

    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    const topEl = document.elementFromPoint(centerX, centerY);
    return el.contains(topEl);
}

export function filterOccludedElements(elements) {
    return elements.filter(element => {
        try {
            const el = element.object;
            
            if (!el) {
                console.warn('Element not found for occlusion check:', element.selector);
                return false;
            }
            
            return isTrulyClickable(el);
        } catch (e) {
            console.warn('Error checking occlusion for element:', element.selector, e);
            return false;
        }
    });
}

// Function to transform top-level elements into final structure
export function transformTopLevelElements(elements, config = null) {
    // Check if elements is null or undefined
    if (!elements) {
        console.warn('No elements provided to transformTopLevelElements');
        return [];
    }

    // Handle the new structure where elements is a Map with key-value pairs
    if (!(elements instanceof Map)) {
        console.warn('Expected elements to be a Map, got:', typeof elements);
        return [];
    }
    
    // Transform and score each element directly from the Map
    const transformedElements = Array.from(elements.entries()).map(([key, element]) => {
        if (!element) return null;

        // 1. Find the best type based on getInverseElementRank
        let bestType = null;
        let bestRank = Infinity;
        let bestAction = null;
        
        // Ensure actions is an array
        const actions = Array.isArray(element.actions) ? element.actions : [];
        
        for (const action of actions) {
            try {
                // Use the DOM element directly from action.object
                const actionEl = action.object;
                if (!actionEl) {
                    console.warn('No DOM element found for action:', action.selector);
                    continue;
                }
                
                const type = getElementType(actionEl);
                const rank = getInverseElementRank(type);
                
                if (rank < bestRank) {
                    bestRank = rank;
                    bestType = type;
                    bestAction = action;
                }
            } catch (e) {
                console.warn('Error processing action:', action?.selector, e);
            }
        }

        // 2. Create normalized bounding box
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const bbox = {
            x: (element.left || 0) / viewportWidth,
            y: (element.top || 0) / viewportHeight,
            w: (element.width || 0) / viewportWidth,
            h: (element.height || 0) / viewportHeight
        };

        // 3. Get selector from best action
        const selector = bestAction?.selector || '';

        // 4. Get attributes from best action
        const attributes = bestAction?.attributes || {};

        // 5. Combine text from all actions
        const text = actions
            .map(action => action.text?.trim())
            .filter(Boolean)
            .join(' | ');

        // 6. Build important text section
        let importantText = '';
        
        // First add text from high-priority attributes
        const highPriorityTexts = [];
        for (const action of actions) {
            try {
                // Use the DOM element directly from action.object
                const actionEl = action.object;
                if (!actionEl) {
                    console.warn('No DOM element found for important text:', action.selector);
                    continue;
                }

                // Check ATTRIBUTE_WEIGHTS attributes
                for (const [attr, weight] of Object.entries(ATTRIBUTE_WEIGHTS)) {
                    if (weight >= 7 && actionEl.hasAttribute(attr)) {
                        const value = actionEl.getAttribute(attr);
                        if (value) highPriorityTexts.push(value);
                    }
                }

                // Check ARIA_WEIGHTS attributes
                for (const [attr, weight] of Object.entries(ARIA_WEIGHTS)) {
                    if (weight >= 7 && actionEl.hasAttribute(attr)) {
                        const value = actionEl.getAttribute(attr);
                        if (value) highPriorityTexts.push(value);
                    }
                }
            } catch (e) {
                console.warn('Error processing action for important text:', action?.selector, e);
            }
        }

        // Add high priority texts
        if (highPriorityTexts.length > 0) {
            importantText += highPriorityTexts.join(' | ');
        }

        // Then add importantText from actions
        const actionTexts = actions
            .map(action => action.importantText)
            .filter(Boolean)
            .flat()
            .filter(Boolean);

        if (actionTexts.length > 0) {
            if (importantText) importantText += ' | ';
            importantText += actionTexts.join(' | ');
        }

        // 7. Gather downstream label/text context under the chosen action element
        const labelContext = (bestAction && bestAction.object)
            ? getDownstreamLabelText(bestAction.object, { maxNodes: 50, maxChars: 300, includeSelf: false })
            : '';

        // Prepend a short version of labelContext (max 20 chars) to importantText
        const shortCtx = (labelContext || '').slice(0, 50);
        if (shortCtx) {
            importantText = importantText ? `${shortCtx} | ${importantText}` : shortCtx;
        }

        // Create the base action object
        const baseAction = {
            type: bestType || 'OTHER',
            bbox,
            selector,
            attributes,
            text,
            importantText,
            score: element.scores?.total || 0,
            object: key
        };

        return baseAction;
    }).filter(Boolean); // Remove any null elements

    return transformedElements.sort((a, b) => b.score - a.score);
}

export function filterActionFields(action, config = null) {
    if (!config || !config.action_filters) {
        return action; // Return unchanged if no config
    }

    const filters = config.action_filters;
    const includeFields = filters.include_fields || [];
    const excludeFields = filters.exclude_fields || [];
    const importantTextMaxLength = filters.important_text_max_length || 250;
    const trimTextLength = filters.trim_text_to_length || 100;
    const filteredAction = {};

    // Process each field based on include/exclude rules
    for (const [key, value] of Object.entries(action)) {
        // Skip if field is explicitly excluded
        if (excludeFields.includes(key)) {
            continue;
        }

        // Include if no include_fields specified (include all) or if field is in include list
        if (includeFields.length === 0 || includeFields.includes(key)) {
            let processedValue = value;

            // Apply text length limits
            if (key === 'importantText' && typeof value === 'string') {
                processedValue = value.slice(0, importantTextMaxLength);
            } else if (key === 'text' && typeof value === 'string') {
                processedValue = value.slice(0, trimTextLength);
            }

            filteredAction[key] = processedValue;
        }
    }

    return filteredAction;
}