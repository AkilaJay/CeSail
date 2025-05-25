import asyncio
import os
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page
from .types import ElementInfo, Action, ActionType, PageAnalysis
import gc

class PageAnalyzer:
    def __init__(self):
        self.browser = None
        self.page = None
        self._js_extractor = None
        self._playwright = None

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def analyze_page(self, url: str) -> Dict[str, Any]:
        """Analyze a page and return comprehensive data about its structure and content."""
        if not self.page:
            raise RuntimeError("PageAnalyzer must be used as an async context manager")

        # Navigate to the page
        await self.page.goto(url, wait_until='networkidle')
        
        # Extract all page data
        page_data = await self._extract_page_data()
        
        # Generate actions for interactive elements
        actions = await self._generate_actions(page_data.get('actions', []))
        
        # Add actions to the page data
        page_data['actions'] = actions
        
        return page_data

    async def _extract_page_data(self) -> Dict[str, Any]:
        """Extract comprehensive data about the page structure and content."""
        if not self._js_extractor:
            self._js_extractor = await self._load_js_extractor()
        
        return await self.page.evaluate(self._js_extractor)

    async def _generate_actions(self, elements: List[Dict[str, Any]]) -> List[Action]:
        """Generate possible actions for interactive elements."""
        actions = []
        
        for element in elements:
            if not element.get('interactive'):
                continue
                
            element_type = element.get('type')
            if not element_type:
                continue
                
            # Generate actions based on element type
            if element_type == 'link':
                actions.extend([
                    Action(
                        type=ActionType.CLICK,
                        description=f"Click {element.get('text', 'link')}",
                        confidence=0.9
                    ),
                    Action(
                        type=ActionType.HOVER,
                        description=f"Hover over {element.get('text', 'link')}",
                        confidence=0.8
                    )
                ])
            elif element_type == 'button':
                actions.extend([
                    Action(
                        type=ActionType.CLICK,
                        description=f"Click {element.get('text', 'button')}",
                        confidence=0.9
                    ),
                    Action(
                        type=ActionType.HOVER,
                        description=f"Hover over {element.get('text', 'button')}",
                        confidence=0.8
                    )
                ])
            elif element_type == 'input':
                input_type = element.get('attributes', {}).get('type', 'text')
                if input_type in ['text', 'email', 'password', 'number']:
                    actions.append(Action(
                        type=ActionType.TYPE,
                        description=f"Type into {element.get('attributes', {}).get('placeholder', 'input field')}",
                        confidence=0.8
                    ))
                elif input_type == 'checkbox':
                    actions.append(Action(
                        type=ActionType.CLICK,
                        description=f"Toggle {element.get('attributes', {}).get('name', 'checkbox')}",
                        confidence=0.9
                    ))
                elif input_type == 'radio':
                    actions.append(Action(
                        type=ActionType.CLICK,
                        description=f"Select {element.get('attributes', {}).get('name', 'radio button')}",
                        confidence=0.9
                    ))
            elif element_type == 'select':
                actions.append(Action(
                    type=ActionType.SELECT,
                    description=f"Select option from {element.get('attributes', {}).get('name', 'dropdown')}",
                    confidence=0.8
                ))
            elif element_type == 'textarea':
                actions.append(Action(
                    type=ActionType.TYPE,
                    description=f"Type into {element.get('attributes', {}).get('placeholder', 'text area')}",
                    confidence=0.8
                ))
        
        # Add global actions
        actions.extend([
            Action(
                type=ActionType.BACK,
                description="Go back in browser history",
                confidence=1.0
            ),
            Action(
                type=ActionType.FORWARD,
                description="Go forward in browser history",
                confidence=1.0
            ),
            Action(
                type=ActionType.SCREENSHOT,
                description="Take screenshot of viewport",
                confidence=1.0
            ),
            Action(
                type=ActionType.EVALUATE,
                description="Execute JavaScript",
                confidence=0.5
            )
        ])
        
        return actions

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
            print("Starting element extraction...")
            elements = await asyncio.wait_for(
                self.page.evaluate("extractElements()"),
                timeout=30.0
            )
            print(f"Extracted {len(elements) if elements else 0} elements")
            return elements
        except asyncio.TimeoutError:
            print("Warning: Element extraction timed out")
            return []
        except Exception as e:
            print(f"Error during element extraction: {str(e)}")
            return []

    def _convert_to_elements(self, elements_data: List[Dict[str, Any]]) -> List[ElementInfo]:
        """Convert raw element data to ElementInfo objects."""
        if not elements_data:
            print("No elements data to convert")
            return []
            
        print(f"Converting {len(elements_data)} elements...")
            
        def convert_element(data: Dict[str, Any]) -> ElementInfo:
            # Handle case where data might be a string
            if isinstance(data, str):
                print(f"Skipping string data: {data}")
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
                print(f"Error converting element: {str(e)}")
                print(f"Element data: {data}")
                return None
            
        converted = [elem for elem in (convert_element(elem) for elem in elements_data) if elem is not None]
        print(f"Successfully converted {len(converted)} elements")
        return converted
