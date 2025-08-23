from typing import List, Optional, Dict, Any
from playwright.async_api import Page
import asyncio
import logging
import time

logger = logging.getLogger(__name__)

class EfficientIdleWatcher:
    """Efficient page idle detection using DOMContentLoaded + MutationObserver + viewport filtering."""
    
    def __init__(self, page: Page, mutation_timeout_ms: int = 300, config: Dict[str, Any] = None):
        self.page = page
        self.mutation_timeout_ms = mutation_timeout_ms
        self.config = config or {}
        self._cleanup_handle = None
        self._promise = None

    def __await__(self):
        """Make the class awaitable - returns a promise that resolves when page is ready."""
        if self._promise is None:
            self._promise = self._create_promise()
        return self._promise.__await__()

    async def _create_promise(self):
        """Create the promise that waits for page to be ready."""
        logger.debug("Starting efficient page ready detection")
        
        # Step 1: Wait for DOMContentLoaded
        await self.wait_for_dom_content_loaded()
        
        # Step 2: Wait for visible mutations to settle
        await self.wait_for_visible_mutations()
        
        logger.debug("Page is ready for analysis")
        return self

    async def wait_for_dom_content_loaded(self):
        """Wait for DOMContentLoaded event."""
        logger.debug("Waiting for DOMContentLoaded")
        await self.page.wait_for_load_state("domcontentloaded")
        logger.debug("DOMContentLoaded fired")

    async def wait_for_visible_mutations(self):
        """Wait for DOM mutations to settle using a short-lived MutationObserver."""
        logger.debug(f"Waiting for visible mutations to settle (timeout: {self.mutation_timeout_ms}ms)")
        try:
            # Check if console logging is enabled
            enable_console_logging = self.config.get("global", {}).get("enable_console_logging", True)
            
            await self.page.evaluate(f"""
                async () => {{
                    let timer;
                    let resizeTimer;
                    const root = document.scrollingElement || document.documentElement;
                    const enableConsoleLogging = {str(enable_console_logging).lower()};
                    
                    // Helper function to check if element is in viewport
                    function isInViewport(el) {{
                        try {{
                            const r = el.getBoundingClientRect();
                            return r.bottom >= 0 &&
                                   r.right >= 0 &&
                                   r.top <= window.innerHeight &&
                                   r.left <= window.innerWidth &&
                                   r.width > 0 &&
                                   r.height > 0;
                        }} catch (e) {{
                            return false;
                        }}
                    }}
                    
                    // Optimized function to check if node or its descendants are visible
                    function hasVisibleContent(node) {{
                        if (node.nodeType !== Node.ELEMENT_NODE) return false;
                        
                        // Check if the node itself is in viewport
                        if (isInViewport(node)) return true;
                        
                        // Check if any direct children are in viewport (simple and fast)
                        const children = node.children;
                        for (let i = 0; i < children.length; i++) {{
                            if (isInViewport(children[i])) return true;
                        }}
                        
                        return false;
                    }}
                    
                    await new Promise(resolve => {{
                        let observer = null;
                        let done = false;
                        
                        function cleanup() {{
                            if (observer) observer.disconnect();
                            window.removeEventListener('resize', handleResize);
                        }}
                        
                        function finish() {{
                            if (done) return;
                            done = true;
                            cleanup();
                            resolve();
                        }}
                        
                        function startObserver() {{
                            if (observer) observer.disconnect();
                            
                            observer = new MutationObserver(muts => {{
                                // Clear timer once per batch
                                clearTimeout(timer);
                                
                                // Scan mutations for visible changes
                                for (const mutation of muts) {{
                                    if (mutation.type === 'childList' && mutation.addedNodes.length) {{
                                        for (const node of mutation.addedNodes) {{
                                            if (hasVisibleContent(node)) {{
                                                // Visible change detected: restart settle timer and exit early
                                                timer = setTimeout(finish, {self.mutation_timeout_ms});
                                                return; // Exit early - no need to check more nodes
                                            }}
                                        }}
                                    }} else if (mutation.type === 'attributes') {{
                                        const targetEl = mutation.target && mutation.target.nodeType === Node.ELEMENT_NODE ? mutation.target : null;
                                        if (targetEl && hasVisibleContent(targetEl)) {{
                                            timer = setTimeout(finish, {self.mutation_timeout_ms});
                                            return;
                                        }}
                                    }} else if (mutation.type === 'characterData') {{
                                        const parentEl = mutation.target && mutation.target.parentElement ? mutation.target.parentElement : null;
                                        if (parentEl && hasVisibleContent(parentEl)) {{
                                            timer = setTimeout(finish, {self.mutation_timeout_ms});
                                            return;
                                        }}
                                    }}
                                }}
                                
                                // No visible changes in this batch, set timer
                                timer = setTimeout(finish, {self.mutation_timeout_ms});
                            }});
                            
                            observer.observe(root, {{
                                childList: true,
                                subtree: true,
                                attributes: true,
                                characterData: true
                            }});
                        }}
                        
                        // Handle window resize events
                        function handleResize() {{
                            clearTimeout(resizeTimer);
                            resizeTimer = setTimeout(() => {{
                                // Restart observer after resize settles
                                startObserver();
                            }}, 100);
                        }}
                        
                        window.addEventListener('resize', handleResize);
                        if (enableConsoleLogging) console.log("Resized event listener added");
                        // Start initial observer
                        startObserver();

                        if (enableConsoleLogging) console.log("Visible mutations settled");
                        
                        // Fallback if no visible mutations ever fire
                        timer = setTimeout(finish, {self.mutation_timeout_ms + 50});
                    }});
                }}
            """)
            logger.debug("Visible mutations settled")
        except Exception as e:
            logger.warning(f"Error in mutation observer: {str(e)}")

    async def get_visible_actions(self) -> List[Dict[str, Any]]:
        """Get only in-viewport interactive elements."""
        logger.debug("Getting visible actions")
        
        try:
            visible_actions = await self.page.evaluate("""
                () => {
                    const selectors = 'button, a, input, [role="button"], [role="link"], [role="menuitem"], [tabindex]';
                    const elements = document.querySelectorAll(selectors);
                    
                    return Array.from(elements).filter(el => {
                        try {
                            const r = el.getBoundingClientRect();
                            return r.bottom >= 0 &&
                                   r.right >= 0 &&
                                   r.top <= window.innerHeight &&
                                   r.left <= window.innerWidth &&
                                   r.width > 0 &&
                                   r.height > 0;
                        } catch (e) {
                            // Skip elements that can't be measured
                            return false;
                        }
                    }).map(el => {
                        try {
                            const r = el.getBoundingClientRect();
                            return {
                                tagName: el.tagName.toLowerCase(),
                                text: el.innerText.trim() || el.textContent.trim(),
                                role: el.getAttribute('role'),
                                type: el.getAttribute('type'),
                                href: el.getAttribute('href'),
                                ariaLabel: el.getAttribute('aria-label'),
                                title: el.getAttribute('title'),
                                tabIndex: el.getAttribute('tabindex'),
                                disabled: el.hasAttribute('disabled'),
                                visible: true,
                                bounds: {
                                    top: r.top,
                                    left: r.left,
                                    width: r.width,
                                    height: r.height
                                }
                            };
                        } catch (e) {
                            // Return basic info if bounds can't be calculated
                            return {
                                tagName: el.tagName.toLowerCase(),
                                text: el.innerText.trim() || el.textContent.trim(),
                                role: el.getAttribute('role'),
                                type: el.getAttribute('type'),
                                href: el.getAttribute('href'),
                                ariaLabel: el.getAttribute('aria-label'),
                                title: el.getAttribute('title'),
                                tabIndex: el.getAttribute('tabindex'),
                                disabled: el.hasAttribute('disabled'),
                                visible: true,
                                bounds: null
                            };
                        }
                    });
                }
            """)
            
            logger.debug(f"Found {len(visible_actions)} visible actions")
            return visible_actions
            
        except Exception as e:
            logger.error(f"Error getting visible actions: {str(e)}")
            return []

    async def get_page_state(self) -> Dict[str, Any]:
        """Get current page state including visible actions."""
        visible_actions = await self.get_visible_actions()
        
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "visible_actions": visible_actions,
            "viewport": await self.page.evaluate("""
                () => ({
                    width: window.innerWidth,
                    height: window.innerHeight
                })
            """),
            "timestamp": time.time()
        }

    async def stop(self):
        """Clean up any resources."""
        logger.debug("Stopping efficient idle watcher")
        if self._cleanup_handle:
            await self._cleanup_handle.dispose()


class ViewportAwareIdleWatcher:
    """Enhanced idle watcher that focuses on viewport-visible content."""
    
    def __init__(self, page: Page, mutation_timeout_ms: int = 300, config: Dict[str, Any] = None):
        self.page = page
        self.mutation_timeout_ms = mutation_timeout_ms
        self.watcher = EfficientIdleWatcher(page, mutation_timeout_ms, config)

    def __await__(self):
        """Make the class awaitable."""
        return self.watcher.__await__()

    async def wait_for_quiescence(self, timeout_ms: int = 10000):
        """Wait for page to be quiescent using the efficient approach."""
        logger.debug(f"Waiting for page quiescence (timeout: {timeout_ms}ms)")
        
        try:
            await asyncio.wait_for(
                self.watcher,
                timeout=timeout_ms / 1000
            )
            logger.debug("Page is quiescent")
        except asyncio.TimeoutError:
            logger.warning(f"Page did not become quiescent within {timeout_ms}ms")
            # Continue anyway - we'll work with what we have
        except Exception as e:
            logger.error(f"Error waiting for quiescence: {str(e)}")

    async def get_visible_elements(self) -> List[Dict[str, Any]]:
        """Get all visible interactive elements in the viewport."""
        return await self.watcher.get_visible_actions()

    async def analyze_page(self) -> Dict[str, Any]:
        """Complete page analysis using the efficient approach."""
        visible_actions = await self.watcher.get_visible_actions()
        
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "visible_actions": visible_actions,
            "viewport": await self.page.evaluate("""
                () => ({
                    width: window.innerWidth,
                    height: window.innerHeight
                })
            """),
            "timestamp": time.time()
        }


# Backward compatibility functions
async def wait_for_page_quiescence(page: Page, idle_ms: int = 300, skip_urls: Optional[List[str]] = None, timeout_ms: int = 10000, config: Dict[str, Any] = None):
    """Backward compatibility function - now uses the efficient approach."""
    logger.debug("Using efficient page quiescence detection")
    watcher = ViewportAwareIdleWatcher(page, mutation_timeout_ms=idle_ms, config=config)
    await watcher.wait_for_quiescence(timeout_ms)
    return await watcher.get_visible_elements()

# Convenience function for Promise-style usage
def wait_for_page_ready(page: Page, mutation_timeout_ms: int = 300, config: Dict[str, Any] = None):
    """Create a Promise-like object that waits for page to be ready."""
    return EfficientIdleWatcher(page, mutation_timeout_ms, config)


# Legacy classes for backward compatibility
class IdleWatcher:
    """Legacy network idle watcher - kept for backward compatibility."""
    
    def __init__(self, page: Page, idle_time_ms: int = 300, skip_urls: Optional[List[str]] = None):
        logger.warning("IdleWatcher is deprecated. Use EfficientIdleWatcher instead.")
        self.page = page
        self.idle_time_ms = idle_time_ms
        self.skip_urls = skip_urls or []

    async def start(self):
        logger.warning("IdleWatcher.start() is deprecated")
        pass

    async def wait_network_idle(self):
        logger.warning("IdleWatcher.wait_network_idle() is deprecated")
        return True

    async def stop(self):
        logger.warning("IdleWatcher.stop() is deprecated")
        pass


class DOMIdleWatcher:
    """Legacy DOM idle watcher - kept for backward compatibility."""
    
    def __init__(self, page: Page, idle_time_ms: int = 300):
        logger.warning("DOMIdleWatcher is deprecated. Use EfficientIdleWatcher instead.")
        self.page = page
        self.idle_time_ms = idle_time_ms

    async def start(self):
        logger.warning("DOMIdleWatcher.start() is deprecated")
        pass

    async def wait_dom_idle(self):
        logger.warning("DOMIdleWatcher.wait_dom_idle() is deprecated")
        return True

    async def stop(self):
        logger.warning("DOMIdleWatcher.stop() is deprecated")
        pass 