import { getElementType, getAttributes } from './utility-functions';
import { ARIA_WEIGHTS, STYLE_WEIGHTS, ATTRIBUTE_WEIGHTS } from './constants';


// Function to get all top-level elements
export function getTopLevelElements(dfsGroups) {
    try {
        const topLevelElements = [];
        for (const [key, element] of dfsGroups.entries()) {
            topLevelElements.push(scoreTopLevelElement(element));
        }
        return dfsGroups;
    } catch (e) {
        console.warn('Error in getTopLevelElements:', e);
        return [];
    }
}

// Function to normalize and clean important text
function normalizeImportantText(impText) {
    // Handle case where impText is not an array
    if (!Array.isArray(impText)) {
        if (typeof impText === 'string') {
            return [impText.trim()];
        }
        return [];
    }

    // impText = [ mainText: string, aux: nested array ]
    const [ mainText, ...aux ] = impText;

    // 1A) Clean the main text
    const cleanedMain = (mainText || '')
        .replace(/\s+/g, ' ')        // collapse whitespace
        .trim();                     // remove leading/trailing

    // 1B) Flatten & clean aux text
    const flatten = arr => {
        if (!Array.isArray(arr)) return [];
        return arr.reduce((acc, v) => {
            if (Array.isArray(v)) return acc.concat(flatten(v));
            if (typeof v === 'string') return acc.concat(v.trim());
            return acc;
        }, []);
    };

    const cleanedAux = flatten(aux)
        .map(s => s.replace(/\s+/g, ' ').trim())
        .filter(Boolean);            // drop empty strings

    return [ cleanedMain, ...cleanedAux ];
}

// Function to tokenize text into unique words
function tokenize(texts) {
    const tokens = new Set();
    for (const t of texts) {
        t.split(/\s+/).forEach(w => {
            const w0 = w.toLowerCase().replace(/[^a-z0-9]/g, '');
            if (w0) tokens.add(w0);
        });
    }
    return Array.from(tokens);
}

// Function to score important text based on various heuristics
function scoreImportantText(impText) {
    const cleaned = normalizeImportantText(impText);
    if (cleaned.length === 0) return 0;

    // A) Main text length
    const mainWords = cleaned[0].split(' ').length;
    const mainScore = Math.min(mainWords / 5, 1);  // up to 5 words → max 1.0

    // B) Aux text bonus
    const auxBonus = (cleaned.length - 1) * 0.1;    // each non-empty aux line +0.1

    // C) Unique token richness
    const unique = tokenize(cleaned).length;
    const richnessScore = Math.min(unique / 10, 1); // 10 unique tokens → max 1.0
    
    // D) Penalize repetition (if main repeats same word 3+ times)
    const repeats = (cleaned[0].match(/\b(\w+)\b.*\b\1\b/) ? 1 : 0);
    const repetitionPenalty = repeats * -0.5;      // if repetition detected, −0.5

    // Calculate raw score (0-3 range)
    const rawScore = mainScore + auxBonus + richnessScore + repetitionPenalty;
    
    // Normalize to -1 to 1 range
    // Using a sigmoid-like function with a scaling factor of 1.5
    // This gives a good spread for scores between 0 and 3
    const normalizedScore = (2 / (1 + Math.exp(-rawScore/1.5))) - 1;
    
    return normalizedScore;
}

// Function to score an element based on its ARIA attributes
function scoreElementByAria(el) {
    let score = 0;
    for (const [attr, weight] of Object.entries(ARIA_WEIGHTS)) {
        if (el.hasAttribute(attr) && el.getAttribute(attr)?.trim()) {
            score += weight;
        }
    }

    // Normalize score to -1 to 1 range
    // The raw score typically ranges from 0 to 23 (sum of all ARIA_WEIGHTS)
    // Using a sigmoid-like function with a scaling factor of 10
    const normalizedScore = (2 / (1 + Math.exp(-score/10))) - 1;
    
    return normalizedScore;
}

// Function to score an element based on its computed styles
function scoreElementByStyle(el) {
    const style = window.getComputedStyle(el);
    let score = 0;

    // 1) display
    const disp = style.display || 'block';
    score += STYLE_WEIGHTS.display[disp] ?? 0;

    // 2) visibility
    const vis = style.visibility || 'visible';
    score += STYLE_WEIGHTS.visibility[vis] ?? 0;

    // 3) z-index
    const zi = parseInt(style.zIndex, 10);
    if (!isNaN(zi)) {
        score += zi * STYLE_WEIGHTS.zIndex.weightFactor;
    }

    // Normalize score to -1 to 1 range
    // The raw score typically ranges from -20 to +25
    // Using a sigmoid-like function with a scaling factor of 20
    const normalizedScore = (2 / (1 + Math.exp(-score/20))) - 1;
    
    return normalizedScore;
}

// Function to score an element based on its attributes
function scoreElementByAttributes(attributes) {
    let score = 0;
    
    // Score each attribute
    for (const [name, value] of Object.entries(attributes)) {
        if (name in ATTRIBUTE_WEIGHTS) {
            // Special handling for certain attributes
            if (name === 'tabindex' && value === '-1') {
                score -= 5; // Penalize negative tabindex
            } else if (name === 'class') {
                // Add points for each class (up to a limit)
                const classCount = value.split(' ').length;
                score += Math.min(classCount * 2, 10); // Cap at 10 points for classes
            } else {
                score += ATTRIBUTE_WEIGHTS[name];
            }
        }
    }

    // Normalize score to -1 to 1 range
    // Using a sigmoid-like function with a scaling factor of 15
    // This gives a good spread for scores between -10 and +30
    const normalizedScore = (2 / (1 + Math.exp(-score/15))) - 1;
    
    return normalizedScore;
}

// Function to get inverse rank of element type (0 for highest importance, 28 for lowest)
export function getInverseElementRank(type) {
    const rankMap = {
        'BUTTON': 0,
        'LINK': 1,
        'SELECT': 2,
        'TEXTAREA': 3,
        'INPUT': 4,
        'CHECKBOX': 5,
        'RADIO': 6,
        'TOGGLE': 7,
        'SLIDER': 8,
        'DATEPICKER': 9,
        'FILE_INPUT': 10,
        'TAB': 11,
        'LABEL': 12,
        'IMAGE': 13,
        'VIDEO': 14,
        'AUDIO': 15,
        'SUMMARY': 16,
        'DETAILS': 17,
        'SVG': 18,
        'CANVAS': 19,
        'IFRAME': 20,
        'TABLE': 21,
        'TABLE_ROW': 22,
        'TABLE_CELL': 23,
        'FORM': 24,
        'MENU': 25,
        'MENUITEM': 26,
        'OTHER': 27
    };
    
    // Get the raw rank (0-27)
    const rawRank = rankMap[type] ?? 27;
    
    // Normalize to -1 to 1 range
    // Map 0 (highest importance) to 1, and 27 (lowest importance) to -1
    const normalizedRank = 1 - (rawRank / 27) * 2;
    
    return normalizedRank;
}

// Function to score an element based on its area
export function scoreElementByArea(element) {
    // Get element dimensions
    let width, height;
    
    if (element instanceof Element) {
        // If it's a DOM element, use getBoundingClientRect
        const rect = element.getBoundingClientRect();
        width = rect.width;
        height = rect.height;
    } else if (element && typeof element === 'object') {
        // If it's a plain object with width/height properties
        width = element.width;
        height = element.height;
    } else {
        // Invalid input, return neutral score
        return 0;
    }

    // Calculate viewport area
    const viewportArea = window.innerWidth * window.innerHeight;
    const ratio = (width * height) / viewportArea;

    // Shift sigmoid to center at 10% viewport area
    const threshold = 0.10;  // Center point (10% of viewport)
    const steepness = 50;    // Controls how quickly the score transitions
    const x = (ratio - threshold) * steepness;

    // Normalize to [-1, 1] range
    // This gives:
    // - ratio < 1% → score ≈ -1
    // - ratio ≈ 10% → score ≈ 0
    // - ratio > 10% → score ≈ +1
    const score = 2 / (1 + Math.exp(-x)) - 1;
    
    return score;
}

// Function to score a top-level element based on its actions
export function scoreTopLevelElement(element) {
    if (!element || !element.actions || !element.actions.length) {
        // Add default scores to the existing element
        element.scores = {
            elementRank: 0,
            attributes: 0,
            style: 0,
            aria: 0,
            semanticText: 0,
            area: 0,
            total: 0
        };
        return element;
    }

    // Initialize scores
    let elementRankScore = 0;
    let attributesScore = 0;
    let styleScore = 0;
    let ariaScore = 0;
    let semanticTextScore = 0;
    let areaScore = scoreElementByArea(element);

    // Score each action
    for (const action of element.actions) {
        try {            
            const actionEl = action.object;
            if (!actionEl) {
                console.warn('Element not found for selector in scoring:', action.selector);
                continue;
            }

            // Get element type and rank
            const type = getElementType(actionEl);
            elementRankScore = Math.max(elementRankScore, getInverseElementRank(type));

            // Get attribute score
            const attributes = getAttributes(actionEl);
            attributesScore = Math.max(attributesScore, scoreElementByAttributes(attributes));

            // Get style score
            styleScore = Math.max(styleScore, scoreElementByStyle(actionEl));

            // Get ARIA score
            ariaScore = Math.max(ariaScore, scoreElementByAria(actionEl));

            // Get semantic text score
            if (action.semanticTextScore !== undefined) {
                semanticTextScore = Math.max(semanticTextScore, action.semanticTextScore);
            }
        } catch (e) {
            console.warn('Error scoring action:', action.selector, e);
        }
    }

    const totalScore = (
        elementRankScore    * 0.30 +   // 20%: type of element (button vs. link vs. form field)
        attributesScore     * 0.10 +   // 10%: IDs, data‑hooks, onclick, etc.
        styleScore          * 0.10 +   // 10%: display/visibility/z‑index
        ariaScore           * 0.10 +   // 10%: aria‑label, aria‑describedby, etc.
        semanticTextScore   * 0.20 +   // 20%: label richness & importantText
        areaScore           * 0.20     // 30%: on‑screen footprint
      );

    // Add scores directly to the existing element
    element.scores = {
        elementRank: elementRankScore,
        attributes: attributesScore,
        style: styleScore,
        aria: ariaScore,
        semanticText: semanticTextScore,
        area: areaScore,
        total: totalScore
    };

    return element;
}