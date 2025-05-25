from typing import Optional, Dict, Any
from .page_analyzer import PageAnalyzer
from .sensitive_handler import SensitiveHandler
from .types import ActionGraph, PageAnalysis

class GraphGenerator:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self._page_analyzer: Optional[PageAnalyzer] = None
        self._sensitive_handler = SensitiveHandler()

    async def __aenter__(self):
        self._page_analyzer = PageAnalyzer(headless=self.headless)
        await self._page_analyzer.init()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._page_analyzer:
            await self._page_analyzer.close()

    async def generate_graph(self, url: str) -> ActionGraph:
        """Generate an action graph for the given URL."""
        if not self._page_analyzer:
            self._page_analyzer = PageAnalyzer(headless=self.headless)
            await self._page_analyzer.init()

        try:
            # Analyze the page
            analysis = await self._page_analyzer.analyze_page(url)
            
            # Create initial action graph
            action_graph = ActionGraph(
                url=url,
                nodes=analysis.elements,
                edges=analysis.actions,
                metadata=analysis.metadata
            )
            
            # Process sensitive elements
            processed_graph = self._sensitive_handler.process_action_graph(action_graph)
            
            return processed_graph
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate action graph: {str(e)}")

    async def close(self):
        """Close the page analyzer and cleanup resources."""
        if self._page_analyzer:
            await self._page_analyzer.close()
            self._page_analyzer = None
