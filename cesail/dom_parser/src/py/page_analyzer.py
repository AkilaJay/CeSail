import asyncio
import os
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page
from .types import ElementInfo, Action, ActionType, ParsedPage
import gc
import json
import logging

logger = logging.getLogger(__name__)

class PageAnalyzer:
    def __init__(self, page: Page, config: Dict[str, Any] = None, **kwargs):
        self.page = page
        # Merge config and kwargs, with kwargs taking precedence
        self.config = config or {}
        if kwargs:
            self.config.update(kwargs)
        self.browser = None
        self._js_extractor = None
        self._playwright = None

        # Enable console logging only if configured
        if self.config.get("global", {}).get("enable_console_logging", True):
            self.page.on("console", lambda msg: logger.debug(f"Page console: {msg.text}"))

    async def analyze_page(self) -> ParsedPage:
        """Analyze the current page and return comprehensive data about its structure and content."""
        try:
            # Extract all page data
            page_data = await self._extract_page_data()

            # Convert to ParsedPage object
            parsed_page = ParsedPage.from_json(page_data)
            return parsed_page
            
        except Exception as e:
            # Return empty ParsedPage instead of raising
            return ParsedPage.from_json({
                'actions': [],
                'forms': [],
                'meta': {'url': self.page.url, 'error': str(e)},
                'elements': []
            })

    async def get_selector_mapping(self) -> Dict[str, str]:
        """Get the complete mapping between selector IDs and original selectors.
        
        Returns:
            Dictionary mapping selector IDs to original selectors
        """
        if not self.page:
            raise RuntimeError("Page not provided.")
        
        try:
            result = await self.page.evaluate("""
                const mapping = {};
                for (const [selector, id] of window.selectorMap) {
                    mapping[id] = selector;
                }
                return mapping;
            """)
            return result
        except Exception as e:
            logger.error(f"Error getting selector mapping: {e}")
            return {}

    async def get_selector_by_id(self, selector_id: str) -> Optional[str]:
        """Get the original selector string from a selector ID.
        
        Args:
            selector_id: The selector ID (e.g., "1", "2", "3")
            
        Returns:
            The original selector string, or None if not found
        """
        if not self.page:
            raise RuntimeError("Page not provided.")
        
        try:
            result = await self.page.evaluate(f"getSelectorById('{selector_id}')")
            return result
        except Exception as e:
            logger.error(f"Error getting selector by ID '{selector_id}': {e}")
            return None

    async def get_selector_id(self, selector: str) -> Optional[str]:
        """Get the selector ID from an original selector string.
        
        Args:
            selector: The original selector string
            
        Returns:
            The selector ID (e.g., "1", "2", "3"), or None if not found
        """
        if not self.page:
            raise RuntimeError("Page not provided.")
        
        try:
            # Escape the selector for JavaScript evaluation
            escaped_selector = selector.replace("'", "\\'").replace('"', '\\"')
            result = await self.page.evaluate(f"getSelectorId('{escaped_selector}')")
            return result
        except Exception as e:
            logger.error(f"Error getting selector ID for '{selector}': {e}")
            return None

    async def clear_selector_mapping(self) -> None:
        """Clear the selector mapping cache."""
        if not self.page:
            raise RuntimeError("Page not provided.")
        
        try:
            await self.page.evaluate("clearSelectorMapping()")
        except Exception as e:
            logger.error(f"Error clearing selector mapping: {e}")

    async def _extract_page_data(self) -> Dict[str, Any]:
        """Extract comprehensive data about the page structure and content."""
        try:
            logger.debug("Waiting for page to be ready for extraction...")
            # Wait for the page to be at least interactive
            await self.page.wait_for_function(
                'document.readyState === "interactive" || document.readyState === "complete"',
                timeout=30000
            )

            # Call the extractElements function from the global window object with config
            page_data = await asyncio.wait_for(
                self.page.evaluate(f"() => window.extractElements({json.dumps(self.config)})"),
                timeout=30.0
            )

            if not page_data:
                logger.error("No page data extracted")
                return {
                    'meta': {'url': self.page.url},
                    'actions': [],
                    'forms': [],
                    'elements': []
                }
            
            # Ensure all actions have a valid selector
            if 'actions' in page_data:
                for action in page_data['actions']:
                    if not action.get('selector'):
                        action['selector'] = 'body'  # Fallback to body if no selector
            
            return page_data
            
        except asyncio.TimeoutError:
            logger.error("Page data extraction timed out")
            return {
                'meta': {'url': self.page.url},
                'actions': [],
                'forms': [],
                'elements': []
            }
        except Exception as e:
            logger.error(f"Error during page data extraction: {str(e)}")
            return {
                'meta': {'url': self.page.url},
                'actions': [],
                'forms': [],
                'elements': []
            }

    async def _generate_actions(self, elements: List[Dict[str, Any]]) -> List[Action]:
        """Generate possible actions for interactive elements."""
        actions = []
        for element in elements:
            # Get element properties from the passed in element data
            tag_name = element.get('tag', '').lower()
            element_type = element.get('type', '')

            # Get the best selector for this element
            selector = element.get('uniqueId', '') or element.get('selector', '') or element.get('id', '')
            
            # Get element text and attributes
            text = element.get('text', '').strip()
            attributes = element.get('attributes', {})
            
            # Generate actions based on element type
            if tag_name == 'a' or attributes.get('role') == 'link':
                actions.extend([
                    Action(
                        type=ActionType.CLICK,
                        description=f"Click {text or 'link'}",
                        confidence=0.9,
                        element_id=selector,
                        return_format=None
                    ),
                    Action(
                        type=ActionType.HOVER,
                        description=f"Hover over {text or 'link'}",
                        confidence=0.8,
                        element_id=selector,
                        return_format = {
                            "element_id": str,
                            "type": str
                        }
                    )
                ])
            elif tag_name == 'button' or attributes.get('role') == 'button':
                actions.extend([
                    Action(
                        type=ActionType.CLICK,
                        description=f"Click {text or 'button'}",
                        confidence=0.9,
                        element_id=selector,
                        return_format= {
                            "element_id": str,
                            "type": str
                        }
                    ),
                    Action(
                        type=ActionType.HOVER,
                        description=f"Hover over {text or 'button'}",
                        confidence=0.8,
                        element_id=selector,
                        return_format= {
                            "element_id": str,
                            "type": str
                        }
                    )
                ])
            elif tag_name == 'input':
                is_required = attributes.get('required') is not None
                if element_type in ['text', 'email', 'password', 'number', 'search', 'tel', 'url']:
                    placeholder = attributes.get('placeholder', 'input field')
                    desc = f"Type into {placeholder}"
                    if is_required:
                        desc += " (Required)"
                    actions.append(Action(
                        type=ActionType.TYPE,
                        description=desc,
                        confidence=0.8,
                        element_id=selector,
                        return_format={
                            "text_to_type": str,
                            "element_id": str,
                            "type": str
                        }
                    ))
                elif element_type == 'checkbox':
                    name = attributes.get('name', 'checkbox')
                    desc = f"Toggle {name}"
                    if is_required:
                        desc += " (Required)"
                    actions.append(Action(
                        type=ActionType.CHECK,
                        description=desc,
                        confidence=0.9,
                        element_id=selector,
                        return_format= {
                            "element_id": str,
                            "type": str
                        }
                    ))
                elif element_type == 'radio':
                    name = attributes.get('name', 'radio button')
                    desc = f"Select {name}"
                    if is_required:
                        desc += " (Required)"
                    actions.append(Action(
                        type=ActionType.CHECK,
                        description=desc,
                        confidence=0.9,
                        element_id=selector,
                        return_format= {
                            "element_id": str,
                            "type": str
                        }
                    ))
            elif tag_name == 'select':
                # Get all options if present in the element dict
                options = attributes.get('options') or element.get('options')
                is_required = attributes.get('required') is not None
                name = attributes.get('name', 'dropdown')
                desc = f"Select option from {name}. {'Required' if is_required else 'Optional'}. {'Multiple selections allowed' if attributes.get('multiple') else 'Single selection only'}."
                if options:
                    desc += f" Options: {options}"
                actions.append(Action(
                    type=ActionType.SELECT,
                    description=desc,
                    confidence=0.8,
                    element_id=selector,
                    return_format={
                        "options": str,
                        "element_id": str,
                        "type": str
                    }
                ))
            elif tag_name == 'textarea':
                is_required = attributes.get('required') is not None
                placeholder = attributes.get('placeholder', 'text area')
                desc = f"Type into {placeholder}"
                if is_required:
                    desc += " (Required)"
                actions.append(Action(
                    type=ActionType.TYPE,
                    description=desc,
                    confidence=0.8,
                    element_id=selector,
                    return_format={
                        "text_to_type": str,
                        "element_id": str,
                        "type": str
                    }
                ))
            elif tag_name == 'img' and (attributes.get('role') == 'button' or attributes.get('onclick')):
                alt = attributes.get('alt', 'image')
                actions.append(Action(
                    type=ActionType.CLICK,
                    description=f"Click image: {alt}",
                    confidence=0.7,
                    element_id=selector,
                    return_format= {
                        "element_id": str,
                        "type": str
                    }
                ))
            elif tag_name == 'summary':
                actions.append(Action(
                    type=ActionType.CLICK,
                    description=f"Toggle {text or 'summary'} to show/hide content",
                    confidence=0.9,
                    element_id=selector,
                    return_format= {
                        "element_id": str,
                        "type": str
                    }
                ))
            else:
                logger.error(f"Other tag: {tag_name}")
        
        return actions

    async def _get_best_selector(self, element) -> str:
        """Get the best selector for an element using either its attributes or Playwright element."""
        # Handle dictionary input (from JavaScript)
        if isinstance(element, dict):
            # Try to get a unique ID
            if element.get('attributes', {}).get('id'):
                return f"#{element['attributes']['id']}"
            
            # Try to get a unique class
            classes = element.get('attributes', {}).get('class', '').split()
            if classes:
                # Use the first class as it's often the most specific
                return f".{classes[0]}"
            
            # Try to use name attribute for form elements
            if element.get('attributes', {}).get('name'):
                return f'[name="{element["attributes"]["name"]}"]'
            
            # Try to use role attribute
            if element.get('attributes', {}).get('role'):
                return f'[role="{element["attributes"]["role"]}"]'
            
            # Try to use aria-label
            if element.get('attributes', {}).get('aria-label'):
                return f'[aria-label="{element["attributes"]["aria-label"]}"]'
            
            # Try to use text content for elements with unique text
            text = element.get('text', '').strip()
            tag_name = element.get('tag', '').lower()
            if text:
                return f'{tag_name}:has-text("{text}")'
            
            # Fallback to tag name
            return tag_name
            
        # Handle Playwright ElementHandle input
        else:
            # Try to get a unique ID
            id = await element.evaluate('el => el.id')
            if id:
                return f"#{id}"
            
            # Try to get a unique class
            classes = await element.evaluate('el => Array.from(el.classList)')
            if classes:
                # Check if any class is unique
                for class_name in classes:
                    count = await self.page.evaluate(f'document.getElementsByClassName("{class_name}").length')
                    if count == 1:
                        return f".{class_name}"
                
                # If no unique class, use all classes
                return f".{'.'.join(classes)}"
            
            # Try to use name attribute for form elements
            name = await element.evaluate('el => el.name')
            if name:
                return f'[name="{name}"]'
            
            # Try to use role attribute
            role = await element.evaluate('el => el.getAttribute("role")')
            if role:
                return f'[role="{role}"]'
            
            # Try to use aria-label
            aria_label = await element.evaluate('el => el.getAttribute("aria-label")')
            if aria_label:
                return f'[aria-label="{aria-label}"]'
            
            # Try to use text content for elements with unique text
            text = await element.text_content()
            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
            if text:
                text = text.strip()
                if text:
                    # Check if this text is unique
                    count = await self.page.evaluate(f'''() => {{
                        const elements = Array.from(document.querySelectorAll('*'));
                        return elements.filter(el => el.textContent.trim() === "{text}").length;
                    }}''')
                    if count == 1:
                        return f'{tag_name}:has-text("{text}")'
            
            # Fallback to a combination of tag and attributes
            attrs = await element.evaluate('''el => {
                const attrs = [];
                for (const attr of el.attributes) {
                    attrs.push(`[${attr.name}="${attr.value}"]`);
                }
                return attrs.join('');
            }''')
            return f"{tag_name}{attrs}"

    async def _load_js_extractor(self):
        extractor_path = os.path.join(os.path.dirname(__file__), 'extractors.js')
        with open(extractor_path, 'r', encoding='utf-8') as f:
            js_code = f.read()
        # Wrap the code so it returns the result of extractElements()
        return f"{js_code}\nextractElements();"

    async def _extract_elements(self) -> List[Dict[str, Any]]:
        """Extract elements from the page using optimized JavaScript."""
        if not self.page:
            raise RuntimeError("Page not initialized")
            
        # Set timeout for extraction
        try:
            elements = await asyncio.wait_for(
                self.page.evaluate("window.extractElements()"),
                timeout=30.0
            )
            return elements
        except asyncio.TimeoutError:
            logger.error("Element extraction timed out")
            return []
        except Exception as e:
            logger.error(f"Error during element extraction: {str(e)}")
            return []

    def _convert_to_elements(self, elements_data: List[Dict[str, Any]]) -> List[ElementInfo]:
        """Convert raw element data to ElementInfo objects."""
        if not elements_data:
            logger.error("No elements data to convert")
            return []
            
        def convert_element(data: Dict[str, Any]) -> ElementInfo:
            # Handle case where data might be a string
            if isinstance(data, str):
                logger.warning(f"Skipping string data: {data}")
                return None
                
            children = []
            if isinstance(data.get('children'), list):
                children = [child for child in (convert_element(child) for child in data['children']) if child is not None]
                
            try:
                element = ElementInfo(
                    id=data.get('id', ''),
                    type=data.get('type', 'OTHER'),
                    tag=data.get('tag', ''),
                    text=data.get('text'),
                    attributes=data.get('attributes', {}),
                    bounding_box=data.get('bounding_box', {'top': 0, 'left': 0, 'width': 0, 'height': 0}),
                    is_visible=data.get('is_visible', True),
                    is_interactive=data.get('is_interactive', False),
                    is_sensitive=data.get('is_sensitive', False),
                    children=children,
                    aria_role=data.get('aria_role'),
                    input_type=data.get('input_type')
                )
                return element
            except Exception as e:
                logger.error(f"Error converting element: {str(e)}")
                logger.error(f"Element data: {data}")
                return None
            
        converted = [elem for elem in (convert_element(elem) for elem in elements_data) if elem is not None]
        return converted

    async def _generate_forms(self) -> List[Dict[str, Any]]:
        """Extract comprehensive information about forms on the page."""
        forms = []
        
        # Get all form elements
        form_elements = await self.page.query_selector_all('form')
        
        for form in form_elements:
            # Get form attributes
            form_attrs = await form.evaluate('''el => {
                const attrs = {};
                for (const attr of el.attributes) {
                    attrs[attr.name] = attr.value;
                }
                return attrs;
            }''')
            
            # Get form fields (inputs, selects, textareas)
            fields = []
            field_elements = await form.query_selector_all('input, select, textarea')
            
            for field in field_elements:
                # Get field attributes
                field_attrs = await field.evaluate('''el => {
                    const attrs = {};
                    for (const attr of el.attributes) {
                        attrs[attr.name] = attr.value;
                    }
                    return attrs;
                }''')
                
                # Get field type
                tag_name = await field.evaluate('el => el.tagName.toLowerCase()')
                field_type = await field.evaluate('el => el.type ? el.type.toLowerCase() : null')
                
                # Get field options for select elements
                options = []
                if tag_name == 'select':
                    options = await field.evaluate('''el => {
                        return Array.from(el.options).map(opt => ({
                            value: opt.value,
                            text: opt.text
                        }));
                    }''')
                
                # Get the best selector for this field
                selector = await self._get_best_selector(field)
                
                # Create field data
                field_data = {
                    'type': field_type or tag_name,
                    'name': field_attrs.get('name'),
                    'id': field_attrs.get('id'),
                    'placeholder': field_attrs.get('placeholder'),
                    'value': field_attrs.get('value'),
                    'required': field_attrs.get('required') is not None,
                    'pattern': field_attrs.get('pattern'),
                    'min': field_attrs.get('min'),
                    'max': field_attrs.get('max'),
                    'options': options if tag_name == 'select' else None,
                    'selector': selector
                }
                
                if field_type == 'file':
                    field_data['accept'] = await field.get_attribute('accept')
                if field_type == 'select-one':
                    options = await field.query_selector_all('option')
                    field_data['options'] = [{'value': await opt.get_attribute('value'), 'text': await opt.text_content()} for opt in options]
                
                fields.append(field_data)
            
            # Create form data
            form_data = {
                'id': form_attrs.get('id'),
                'name': form_attrs.get('name'),
                'action': form_attrs.get('action'),
                'method': form_attrs.get('method', 'get').lower(),
                'enctype': form_attrs.get('enctype'),
                'fields': fields,
                'selector': await self._get_best_selector(form)
            }
            
            forms.append(form_data)
        
        return forms

    # Getter methods for accessing processing steps
    async def get_raw_actions(self) -> List[Dict[str, Any]]:
        """Get raw actions from the processing pipeline.
        
        Returns:
            List of raw action data
        """
        try:
            result = await self.page.evaluate("getRawActions()")
            return result or []
        except Exception as e:
            logger.error(f"Error getting raw actions: {str(e)}")
            return []

    async def get_grouped_actions(self) -> List[Dict[str, Any]]:
        """Get grouped actions from the processing pipeline.
        
        Returns:
            List of grouped action data
        """
        try:
            result = await self.page.evaluate("getGroupedActions()")
            return result or []
        except Exception as e:
            logger.error(f"Error getting grouped actions: {str(e)}")
            return []

    async def get_scored_actions(self) -> List[Dict[str, Any]]:
        """Get scored actions from the processing pipeline.
        
        Returns:
            List of scored action data
        """
        try:
            result = await self.page.evaluate("getScoredActions()")
            return result or []
        except Exception as e:
            logger.error(f"Error getting scored actions: {str(e)}")
            return []

    async def get_transformed_actions(self) -> List[Dict[str, Any]]:
        """Get transformed actions from the processing pipeline.
        
        Returns:
            List of transformed action data
        """
        try:
            result = await self.page.evaluate("getTransformedActions()")
            return result or []
        except Exception as e:
            logger.error(f"Error getting transformed actions: {str(e)}")
            return []

    async def get_filtered_actions(self) -> List[Dict[str, Any]]:
        """Get filtered actions from the processing pipeline.
        
        Returns:
            List of filtered action data
        """
        try:
            result = await self.page.evaluate("getFilteredActions()")
            return result or []
        except Exception as e:
            logger.error(f"Error getting filtered actions: {str(e)}")
            return []

    async def get_mapped_actions(self) -> List[Dict[str, Any]]:
        """Get mapped actions from the processing pipeline.
        
        Returns:
            List of mapped action data
        """
        try:
            result = await self.page.evaluate("getMappedActions()")
            return result or []
        except Exception as e:
            logger.error(f"Error getting mapped actions: {str(e)}")
            return []

    async def get_field_filtered_actions(self) -> List[Dict[str, Any]]:
        """Get field filtered actions from the processing pipeline.
        
        Returns:
            List of field filtered action data
        """
        try:
            result = await self.page.evaluate("getFieldFilteredActions()")
            return result or []
        except Exception as e:
            logger.error(f"Error getting field filtered actions: {str(e)}")
            return []
