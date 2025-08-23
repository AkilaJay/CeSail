// // Main entry point for DOM Parser - Public API
// // This file serves as the main export for the library

import { extractActions, extractMetaData, extractDocumentOutline, extractForms, extractMedia, extractLinks, extractStructuredData, extractDynamicState, extractLayoutInfo, extractPaginationInfo, extractTextContent } from './action-extraction';
import { isVisible, getComputedStyles, isInteractive, getElementType } from './utility-functions';
import { getPlaywrightStyleSelector } from './selector-extraction';
import { getInverseElementRank, getTopLevelElements } from './scoring';
import { ARIA_WEIGHTS, STYLE_WEIGHTS, ATTRIBUTE_WEIGHTS } from './constants';
import { groupActionableElementsDFS, filterOccludedElements, transformTopLevelElements, filterActionFields } from './filter-elements';
import { clearStyleCache, topLevelElementsCache, clearSelectorMap, selectorMap, clearTopLevelElementsCache, clearSelectorCache, incrementSelectorId} from './cache-manager';
import { clearPerf, printPerfSummary, perfStart, perfEnd, enablePerf, disablePerf, dumpTraceToFile } from './perf';
import { drawBoundingBoxes, toggleVisualization, clearCanvas, drawRuler, drawDot } from './visualizer';


// Function to clean objects for JSON serialization
function cleanForSerialization(obj) {
    if (obj === null || obj === undefined) {
        return obj;
    }
    
    if (typeof obj === 'object') {
        if (Array.isArray(obj)) {
            return obj.map(item => cleanForSerialization(item));
        } else {
            const cleaned = {};
            for (const [key, value] of Object.entries(obj)) {
                // Skip DOM objects and functions
                if (key === 'object' || key === 'element' || key === 'node' || 
                    typeof value === 'function' || 
                    (value && value.nodeType !== undefined)) {
                    continue;
                }
                cleaned[key] = cleanForSerialization(value);
            }
            return cleaned;
        }
    }
    
    return obj;
}

// Custom cleaning function for processing steps that preserves element data
function cleanProcessingStep(obj) {
    if (obj === null || obj === undefined) {
        return obj;
    }
    
    if (typeof obj === 'object') {
        if (Array.isArray(obj)) {
            return obj.map(item => cleanProcessingStep(item));
        } else {
            const cleaned = {};
            for (const [key, value] of Object.entries(obj)) {
                // For processing steps, we want to keep the element data but remove DOM objects
                if (key === 'object' && value && value.nodeType !== undefined) {
                    // Skip DOM objects
                    continue;
                } else if (key === 'element' && value && value.object) {
                    // Keep element data but remove the DOM object
                    const cleanedElement = { ...value };
                    delete cleanedElement.object;
                    cleaned[key] = cleanedElement;
                } else if (typeof value === 'function' || 
                    (value && value.nodeType !== undefined)) {
                    // Skip functions and DOM objects
                    continue;
                } else {
                    cleaned[key] = cleanProcessingStep(value);
                }
            }
            return cleaned;
        }
    }
    
    return obj;
}

// Global storage for processing steps
window.domParserProcessingSteps = {
    rawActions: null,
    groupedActions: null,
    scoredActions: null,
    transformedActions: null,
    filteredActions: null,
    mappedActions: null,
    fieldFilteredActions: null
};

// Helper functions to retrieve processing steps
function getRawActions() {
    return window.domParserProcessingSteps.rawActions;
}

function getGroupedActions() {
    return window.domParserProcessingSteps.groupedActions;
}

function getScoredActions() {
    return window.domParserProcessingSteps.scoredActions;
}

function getTransformedActions() {
    return window.domParserProcessingSteps.transformedActions;
}

function getFilteredActions() {
    return window.domParserProcessingSteps.filteredActions;
}

function getMappedActions() {
    return window.domParserProcessingSteps.mappedActions;
}

function getFieldFilteredActions() {
    return window.domParserProcessingSteps.fieldFilteredActions;
}

// Main extraction function with optimizations
function extractElements(config = null) {
    // Initialize result object
    perfStart('metadata-except-actions', 'Extract all metadata (forms, media, links, etc.) except actions');
    const result = {
        // Individual element extraction parameters
        meta: null,
        outline: null,
        text: null,
        forms: null,
        media: null,
        links: null,
        structuredData: null,
        dynamic: null,
        layout: null,
        pagination: null,
        
        // Only store mapped actions in result
        actions: []
    };

    perfEnd('metadata-except-actions');
    
    // Extract element extraction config
    const elementConfig = config?.element_extraction || {};
    const enableMapping = config?.element_extraction?.actions?.enable_mapping !== false; // Default to true
    const showBoundingBoxes = config?.element_extraction?.actions?.show_bounding_boxes ?? true; // Default to true
    
    // Helper function to check if extraction is enabled
    const shouldExtract = (key) => {
        if (!config) return true; // If no config, extract everything
        return elementConfig[key] !== false; // Default to true if not specified
    };
    
    // Conditionally extract elements based on config
    if (shouldExtract('extract_meta_data')) {
        result.meta = extractMetaData();
    }
    
    if (shouldExtract('extract_document_outline')) {
        result.outline = extractDocumentOutline();
    }
    
    if (shouldExtract('extract_text_content')) {
        result.text = extractTextContent();
    }
    
    if (shouldExtract('extract_forms')) {
        result.forms = extractForms();
    }
    
    if (shouldExtract('extract_media')) {
        result.media = extractMedia();
    }
    
    if (shouldExtract('extract_links')) {
        result.links = extractLinks();
    }
    
    if (shouldExtract('extract_structured_data')) {
        result.structuredData = extractStructuredData();
    }
    
    if (shouldExtract('extract_dynamic_state')) {
        result.dynamic = extractDynamicState();
    }
    
    if (shouldExtract('extract_layout_info')) {
        result.layout = extractLayoutInfo();
    }
    
    if (shouldExtract('extract_pagination_info')) {
        result.pagination = extractPaginationInfo();
    }
    
    // Initialize performance tracking and caches
    enablePerf();
    clearPerf();
    perfStart('extractElementsTotal', 'Perf for the entire extraction');

    // Clear selector mapping at the start of each extraction
    clearSelectorMap();
    clearTopLevelElementsCache();
    clearStyleCache();
    clearSelectorCache();

    // Store all interactive elements for priority filtering
    perfStart('interactiveElements', 'Process interactive elements');
    const interactiveElements = [];

    // Checkpoint 1: Raw actions
    const foundElements = extractActions();
    // Convert Map to array for storage
    const rawArray = Array.from(foundElements.entries()).map(([key, value]) => ({
        key: key,
        element: value
    }));
    
    window.domParserProcessingSteps.rawActions = cleanProcessingStep(rawArray);
    // Process found elements (debug logging removed for cleaner output)

    // Checkpoint 2: Grouped actions
    perfStart('dfsGrouping', 'Group actions using DFS');
    const dfsGroups = groupActionableElementsDFS(foundElements);
    // Convert Map to array for storage
    const groupedArray = Array.from(dfsGroups.entries()).map(([key, value]) => ({
        key: key,
        element: value
    }));
    window.domParserProcessingSteps.groupedActions = cleanProcessingStep(groupedArray);
    perfEnd('dfsGrouping');

    // Checkpoint 3: Scored actions
    perfStart('topLevelElements');
    const scoredElements = getTopLevelElements(dfsGroups);
    // Convert Map to array for storage
    const scoredArray = Array.from(scoredElements.entries()).map(([key, value]) => ({
        key: key,
        element: value
    }));
    window.domParserProcessingSteps.scoredActions = cleanProcessingStep(scoredArray);
    perfEnd('topLevelElements');

    // Checkpoint 4: Transformed actions
    perfStart('transform');
    const finalStructure = transformTopLevelElements(dfsGroups, config);
    window.domParserProcessingSteps.transformedActions = cleanForSerialization(finalStructure);
    perfEnd('transform');
    
    // Checkpoint 5: Filtered actions
    perfStart('occlusionFilter');
    const filteredStructure = filterOccludedElements(finalStructure);
    window.domParserProcessingSteps.filteredActions = cleanForSerialization(filteredStructure);
    perfEnd('occlusionFilter');

    // Checkpoint 6: Mapped actions (final output)
    perfStart('selectorMapping');
    let mappedStructure;
    if (enableMapping){
        mappedStructure = filteredStructure.map(element => {
            const selectorId = getSelectorId(element.selector);
            return {
                ...element,
                selector: selectorId
            };
        });
    } else {
        mappedStructure = filteredStructure;
    }

    window.domParserProcessingSteps.mappedActions = cleanForSerialization(mappedStructure);
    perfEnd('selectorMapping');
    
    // Draw bounding boxes for top-level elements (if enabled)
    if (showBoundingBoxes) {
        perfStart('drawBoundingBoxes');
        drawBoundingBoxes(cleanForSerialization(mappedStructure));
        perfEnd('drawBoundingBoxes');
    }

    // return result;
    // Apply action field filtering to filtered actions
    let fieldFilteredStructure = mappedStructure;
    if (elementConfig && elementConfig.actions && elementConfig.actions.action_filters) {
        fieldFilteredStructure = mappedStructure.map(action => filterActionFields(action, elementConfig.actions));
    }

    window.domParserProcessingSteps.fieldFilteredActions = cleanForSerialization(fieldFilteredStructure);

    result.actions = window.domParserProcessingSteps.fieldFilteredActions;

    perfEnd('extractElementsTotal');

    // Use mapped actions from global storage
    const cleanMappedStructure = window.domParserProcessingSteps.mappedActions || [];

    // Calculate and print the size in KB
    const jsonString = JSON.stringify(cleanMappedStructure);
    const sizeInBytes = new Blob([jsonString]).size;
    const sizeInKB = (sizeInBytes / 1024).toFixed(2);
    console.log(`\nFinal structure size: ${sizeInKB} KB (${sizeInBytes} bytes)`);
    console.log(`Number of elements: ${cleanMappedStructure.length}`);

    // Print all processing steps
    console.log('==========================================');
    console.log('ALL PROCESSING STEPS:');
    console.log('==========================================');
    console.log('Raw Actions Count:', window.domParserProcessingSteps.rawActions?.length || 0);
    console.log('Grouped Actions Count:', window.domParserProcessingSteps.groupedActions?.length || 0);
    console.log('Scored Actions Count:', window.domParserProcessingSteps.scoredActions?.length || 0);
    console.log('Transformed Actions Count:', window.domParserProcessingSteps.transformedActions?.length || 0);
    console.log('Filtered Actions Count:', window.domParserProcessingSteps.filteredActions?.length || 0);
    console.log('Mapped Actions Count:', window.domParserProcessingSteps.mappedActions?.length || 0);
    
    console.log('==========================================');
    console.log('RAW ACTIONS:');
    console.log('==========================================');
    console.log(JSON.stringify(window.domParserProcessingSteps.rawActions, null, 2));
    
    console.log('==========================================');
    console.log('GROUPED ACTIONS:');
    console.log('==========================================');
    console.log(JSON.stringify(window.domParserProcessingSteps.groupedActions, null, 2));
    
    console.log('==========================================');
    console.log('SCORED ACTIONS:');
    console.log('==========================================');
    console.log(JSON.stringify(window.domParserProcessingSteps.scoredActions, null, 2));
    
    console.log('==========================================');
    console.log('TRANSFORMED ACTIONS:');
    console.log('==========================================');
    console.log(JSON.stringify(window.domParserProcessingSteps.transformedActions, null, 2));
    
    console.log('==========================================');
    console.log('FILTERED ACTIONS:');
    console.log('==========================================');
    console.log(JSON.stringify(window.domParserProcessingSteps.filteredActions, null, 2));
    
    console.log('==========================================');
    console.log('MAPPED ACTIONS:');
    console.log('==========================================');
    console.log(JSON.stringify(window.domParserProcessingSteps.mappedActions, null, 2));

    console.log('==========================================');
    console.log('FIELD FILTERED ACTIONS:');
    console.log('==========================================');
    console.log(JSON.stringify(window.domParserProcessingSteps.fieldFilteredActions, null, 2));
    
    printPerfSummary();
    dumpTraceToFile("/tmp/trace.json");
    return result;
}

// // Function to clear the cache
// function clearTopLevelElementsCache() {
//     topLevelElementsCache.clear();
// }

// Global selector mapping
// window.selectorMap = selectorMap;

// Function to get or create selector ID
function getSelectorId(selector) {
    if (!selectorMap.has(selector)) {
        selectorMap.set(selector, incrementSelectorId());
    }
    return String(selectorMap.get(selector));
}

// Function to get selector by ID
function getSelectorById(id) {
    // Convert string ID to integer for comparison
    const numericId = parseInt(id, 10);
    
    for (const [selector, selectorId] of selectorMap) {
        if (selectorId === numericId) {
            return selector;
        }
    }
    return null;
}

// // Public API exports
// export {
//     // Main function
//     extractElements,
//     drawBoundingBoxes,
//     toggleVisualization,
//     clearCanvas,
//     drawRuler,
//     drawDot,
    
//     // // Utility functions
//     // clearTopLevelElementsCache,
//     // transformTopLevelElements,
//     // printProfilingSummary,
//     // profilingData,
//     // groupActionableElementsDFS,
//     // // clearSelectorMapping,
//     getSelectorId,
//     getSelectorById,
    
//     // // Element analysis
//     // isVisible,
//     // getElementType,
//     // isInteractive,
//     // getComputedStyles,
    
//     // // Text extraction
    
//     // extractDocumentOutline,
//     // extractForms,
//     // extractMedia,
//     // extractLinks,
//     // extractStructuredData,
//     // extractDynamicState,
//     // extractLayoutInfo,
//     // extractPaginationInfo,

//     // CONTAINER_CLASSES,
//     // CONTAINER_ATTRS,
// };

// For backward compatibility, also export to window
if (typeof window !== 'undefined') {
    window.extractElements = extractElements;
    window.drawBoundingBoxes = drawBoundingBoxes;
    window.toggleVisualization = toggleVisualization;
    window.clearCanvas = clearCanvas;
    window.getSelectorId = getSelectorId;
    window.getSelectorById = getSelectorById;
    window.drawRuler = drawRuler;
    window.drawDot = drawDot;
    
    // Export helper functions for processing steps
    window.getRawActions = getRawActions;
    window.getGroupedActions = getGroupedActions;
    window.getScoredActions = getScoredActions;
    window.getTransformedActions = getTransformedActions;
    window.getFilteredActions = getFilteredActions;
    window.getMappedActions = getMappedActions;
    window.getFieldFilteredActions = getFieldFilteredActions;
} 