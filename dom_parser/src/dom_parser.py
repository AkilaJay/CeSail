"""
DOM Parser module for extracting and analyzing web page elements
"""

import asyncio
import json
import time
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from .py.page_analyzer import PageAnalyzer
from .py.action_executor import ActionExecutor
from .py.screenshot import ScreenshotTaker
from .py.types import Action, ActionType, ActionResult, ElementInfo, ParsedPage
from .py.idle_watcher import wait_for_page_quiescence, wait_for_page_ready
from .py.config import load_config, get_module_config, validate_config, DEFAULT_CONFIG
# from .extractors import extract_elements_script

logger = logging.getLogger(__name__)

class DOMParser:
    """Main interface for DOM parsing and interaction."""
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        config_file: Optional[str] = None,
        headless: Optional[bool] = None,
        idle_time_ms: Optional[int] = None,
        browser_args: Optional[List[str]] = None,
        bundle_path: Optional[str] = None,
        extra_http_headers: Optional[Dict[str, str]] = None,
        browser_type: Optional[str] = None,
        context_options: Optional[Dict[str, Any]] = None,
        enable_console_logging: Optional[bool] = None,
        playwright: Optional[any] = None,
        browser: Optional[Browser] = None,
        context: Optional[BrowserContext] = None,
    ):
        # Load configuration
        self.config = load_config(config_file, config)
        
        # Override with direct parameters if provided (for backward compatibility)
        if headless is not None:
            self.config["browser"]["headless"] = headless
        if idle_time_ms is not None:
            self.config["idle_watcher"]["default_idle_time_ms"] = idle_time_ms
        if browser_args is not None:
            self.config["browser"]["browser_args"] = browser_args
        if bundle_path is not None:
            self.config["global"]["bundle_path"] = bundle_path
        if extra_http_headers is not None:
            self.config["browser"]["extra_http_headers"] = extra_http_headers
        if browser_type is not None:
            self.config["browser"]["browser_type"] = browser_type
        if context_options is not None:
            self.config["browser"]["context_options"] = context_options
        if enable_console_logging is not None:
            self.config["global"]["enable_console_logging"] = enable_console_logging
        
        # Validate configuration
        validate_config(self.config)
        
        # Configure logging based on config
        log_level = self.config["global"]["log_level"]
        logging.basicConfig(level=getattr(logging, log_level.upper()))
        
        # Extract browser config
        browser_config = self.config["browser"]
        self.headless = browser_config["headless"]
        self.browser_args = browser_config["browser_args"]
        self.bundle_path = Path(self.config["global"]["bundle_path"]) if self.config["global"]["bundle_path"] else Path(__file__).parent.parent / "dist" / "dom-parser.js"
        self.extra_http_headers = browser_config["extra_http_headers"]
        self.browser_type = browser_config["browser_type"]
        self.context_options = browser_config["context_options"]
        self.enable_console_logging = self.config["global"]["enable_console_logging"]
        
        # External resource flags
        self._external_playwright = playwright is not None
        self._external_browser = browser is not None
        self._external_context = context is not None
        
        # Store external instances
        self._playwright = playwright
        self.browser = browser
        self.context = context
        
        # Internal instances (will be created if not provided)
        self.page = None
        self._page_analyzer = None
        self._action_executor = None
        self._screenshot_taker = None

    async def __aenter__(self):
        """Initialize the browser and page when entering the context."""
        if not self._playwright:
            self._playwright = await async_playwright().start()
        if not self.browser:
            browser_launcher = getattr(self._playwright, self.browser_type)
            self.browser = await browser_launcher.launch(
                headless=self.headless,
                args=self.browser_args
            )
        if not self.context:
            self.context = await self.browser.new_context(**self.context_options)
        # Inject DOM parser bundle as an init script so it's available on every page
        if self.bundle_path and self.bundle_path.exists():
            await self.context.add_init_script(path=str(self.bundle_path))
            print("DOM parser bundle injected as init script")
        else:
            print(f"Warning: DOM parser bundle not found at {self.bundle_path}")
        self.page = await self.context.new_page()
        # Set essential headers to appear more like a regular browser
        if self.extra_http_headers:
            await self.page.set_extra_http_headers(self.extra_http_headers)
        
        # Initialize analyzers with their configurations
        page_analyzer_config = get_module_config(self.config, "page_analyzer")
        action_executor_config = get_module_config(self.config, "action_executor")
        screenshot_config = get_module_config(self.config, "screenshot")
        
        self._page_analyzer = PageAnalyzer(self.page, config=self.config, **page_analyzer_config)
        self._action_executor = ActionExecutor(self.page, **action_executor_config)
        self._screenshot_taker = ScreenshotTaker(self.page, **screenshot_config)
        
        return self

    async def __aexit__(self, exc_type, exc, tb):
        # Only close what we created
        if self.page:
            await self.page.close()
        if self.context and not self._external_context:
            await self.context.close()
        if self.browser and not self._external_browser:
            await self.browser.close()
        if self._playwright and not self._external_playwright:
            await self._playwright.stop()

    async def execute_action(
        self,
        action: Action,
        wait_for_idle: bool = True,
        skip_urls: Optional[List[str]] = None,
        translate_element_id: bool = False,
    ) -> ActionResult:
        """Execute an action on the current page, with optional element_id translation.
        Args:
            action: The action to execute
            wait_for_idle: Whether to wait for the page to be idle after the action
            skip_urls: List of URL patterns to ignore when checking for network idle state
            translate_element_id: Whether to translate element_id to a selector
        """
        if not self._action_executor:
            raise RuntimeError("DOMParser not initialized. Use 'async with' context manager.")

        try:
            print("Starting element extraction...")
            await asyncio.wait_for(
                self.page.evaluate("clearCanvas()"),
                timeout=30.0
            )
            print(f"Cleared canvas")
        except asyncio.TimeoutError:
            print("Timeout error during clear canvas")
        except Exception as e:
            print(f"Error during clear canvas: {str(e)}")

        if action.type == ActionType.CUSTOM_CLICK:
            # Convert coordinates if they are from screenshot resolution to actual page resolution
            if hasattr(action, 'metadata') and action.metadata:
                metadata = action.metadata
                x = metadata.get('x')
                y = metadata.get('y')
                if x is not None and y is not None:
                    try:
                        actual_x, actual_y = self._screenshot_taker.convert_coordinates_from_screenshot_to_actual(x, y)
                        logger.info(f"Converted coordinates from ({x}, {y}) to ({actual_x}, {actual_y})")
                        action.metadata['x'] = actual_x
                        action.metadata['y'] = actual_y
                    except Exception as e:
                        logger.warning(f"Error converting coordinates: {e}")

        if translate_element_id and hasattr(action, 'element_id') and action.element_id:
            try:
                selector = await self._page_analyzer.get_selector_by_id(action.element_id)
                action.element_id = selector
            except Exception as e:
                logger.warning(f"Error translating element_id to selector: {e}")
                raise

        result = await self._action_executor.execute_action(action)

        if wait_for_idle:
            logger.info(f"Waiting for page to be idle for {self.config['idle_watcher']['default_idle_time_ms']}ms")
            ready_promise = wait_for_page_ready(self.page, mutation_timeout_ms=self.config['idle_watcher']['default_idle_time_ms'], config=self.config)
            await ready_promise

        return result

    async def analyze_page(self) -> ParsedPage:
        """Analyze the current page and return comprehensive data about its structure and content."""
        if not self._page_analyzer:
            raise RuntimeError("DOMParser not initialized. Use 'async with' context manager.")
        return await self._page_analyzer.analyze_page()

    async def take_screenshot(
        self,
        filepath: Union[str, Path],
        dimensions: Optional[Tuple[int, int]] = None,
        quality: Optional[int] = None,
        format: Optional[str] = None,
        full_page: bool = False,
        clip: Optional[dict] = None,
        omit_background: bool = False,
        return_base64: bool = False
    ) -> str:
        """
        Take a screenshot with configurable parameters
        
        Args:
            filepath: Path where to save the screenshot
            dimensions: Tuple of (width, height) to resize the page before screenshot
            quality: JPEG quality (1-100), only applies to JPEG format
            format: Image format ('jpeg', 'png', 'webp')
            full_page: Whether to take full page screenshot
            clip: Dict with x, y, width, height to clip the screenshot
            omit_background: Whether to omit background (transparent PNG)
            return_base64: Whether to return base64 encoded image instead of filepath
            
        Returns:
            Path to the saved screenshot file or base64 encoded image
        """
        if not self._screenshot_taker:
            raise RuntimeError("DOMParser not initialized. Use 'async with' context manager.")
        
        return await self._screenshot_taker.take_screenshot(
            filepath=filepath,
            dimensions=dimensions,
            quality=quality,
            format=format,
            full_page=full_page,
            clip=clip,
            omit_background=omit_background,
            return_base64=return_base64
        )


    # Debugging methods
    async def get_page_content(self) -> str:
        """Get the current page's HTML content."""
        if not self.page:
            raise RuntimeError("DOMParser not initialized. Use 'async with' context manager.")
        return await self.page.content()
    
    async def get_page(self) -> Page:
        """Get the current page."""
        if not self.page:
            raise RuntimeError("DOMParser not initialized. Use 'async with' context manager.")
        return self.page

    @property
    def page_analyzer(self) -> 'PageAnalyzer':
        """Get the page analyzer instance."""
        if self._page_analyzer is None:
            raise RuntimeError("Page not initialized. Call __aenter__() first.")
        return self._page_analyzer

    @property
    def action_executor(self) -> 'ActionExecutor':
        """Get the action executor instance."""
        if self._action_executor is None:
            raise RuntimeError("Page not initialized. Call __aenter__() first.")
        return self._action_executor

    @property
    def screenshot_taker(self) -> 'ScreenshotTaker':
        """Get the screenshot taker instance."""
        if self._screenshot_taker is None:
            raise RuntimeError("Page not initialized. Call __aenter__() first.")
        return self._screenshot_taker

    def get_available_actions(self) -> Dict[str, Any]:
        """Get comprehensive information about all available action plugins."""
        if self._action_executor is None:
            raise RuntimeError("Page not initialized. Call __aenter__() first.")
        return self._action_executor.get_available_actions()
