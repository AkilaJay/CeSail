"""
Screenshot module for DOM parser
Provides functionality to take screenshots with configurable dimensions and quality
"""

import asyncio
import base64
from pathlib import Path
from typing import Optional, Tuple, Union, Dict
import logging

logger = logging.getLogger(__name__)


class ScreenshotTaker:
    """Class to handle screenshot functionality with configurable parameters"""
    
    def __init__(self, page, **kwargs):
        """
        Initialize the screenshot taker
        
        Args:
            page: Playwright page object
            **kwargs: Configuration parameters
        """
        self.page = page
        # Set defaults from kwargs or use hardcoded defaults
        self.default_quality = kwargs.get('default_quality', 80)
        self.default_format = kwargs.get('default_format', 'jpeg')
        self.original_viewport_size = None
        self.last_requested_size = None
        self.last_screenshot_info = None
    
    async def _store_viewport_info(self, dimensions: Optional[Tuple[int, int]] = None):
        """
        Store original viewport size and requested dimensions
        
        Args:
            dimensions: Requested dimensions for screenshot
        """
        # Store original viewport size if not already stored
        if self.original_viewport_size is None:
            self.original_viewport_size = self.page.viewport_size
            logger.info(f"Stored original viewport size: {self.original_viewport_size}")
        
        # Store requested dimensions
        if dimensions:
            self.last_requested_size = dimensions
            logger.info(f"Stored requested screenshot size: {dimensions}")
        else:
            # If no dimensions specified, use current viewport
            current_viewport = self.page.viewport_size
            self.last_requested_size = (current_viewport['width'], current_viewport['height'])
            logger.info(f"Using current viewport as requested size: {self.last_requested_size}")
    
    def convert_coordinates(
        self, 
        x: float, 
        y: float, 
        from_resolution: Tuple[int, int], 
        to_resolution: Tuple[int, int]
    ) -> Tuple[float, float]:
        """
        Convert coordinates from one resolution to another
        
        Args:
            x: X coordinate in source resolution
            y: Y coordinate in source resolution
            from_resolution: Source resolution (width, height)
            to_resolution: Target resolution (width, height)
            
        Returns:
            Tuple of (x, y) coordinates in target resolution
        """
        from_width, from_height = from_resolution
        to_width, to_height = to_resolution
        
        # Calculate scaling factors
        scale_x = to_width / from_width
        scale_y = to_height / from_height
        
        # Convert coordinates
        new_x = x * scale_x
        new_y = y * scale_y
        
        return (new_x, new_y)
    
    def convert_coordinates_from_screenshot_to_actual(
        self, 
        x: float, 
        y: float
    ) -> Tuple[float, float]:
        """
        Convert coordinates from last screenshot resolution to actual page resolution
        
        Args:
            x: X coordinate in screenshot resolution
            y: Y coordinate in screenshot resolution
            
        Returns:
            Tuple of (x, y) coordinates in actual page resolution
        """
        if not self.last_requested_size or not self.original_viewport_size:
            logger.warning("No viewport information available, returning original coordinates")
            return (x, y)
        
        actual_resolution = (self.original_viewport_size['width'], self.original_viewport_size['height'])
        return self.convert_coordinates(x, y, self.last_requested_size, actual_resolution)
    
    def convert_coordinates_from_actual_to_screenshot(
        self, 
        x: float, 
        y: float
    ) -> Tuple[float, float]:
        """
        Convert coordinates from actual page resolution to last screenshot resolution
        
        Args:
            x: X coordinate in actual page resolution
            y: Y coordinate in actual page resolution
            
        Returns:
            Tuple of (x, y) coordinates in screenshot resolution
        """
        if not self.last_requested_size or not self.original_viewport_size:
            logger.warning("No viewport information available, returning original coordinates")
            return (x, y)
        
        actual_resolution = (self.original_viewport_size['width'], self.original_viewport_size['height'])
        return self.convert_coordinates(x, y, actual_resolution, self.last_requested_size)
    
    def get_viewport_info(self) -> Dict[str, any]:
        """
        Get stored viewport information
        
        Returns:
            Dictionary containing viewport information
        """
        return {
            'original_viewport_size': self.original_viewport_size,
            'last_requested_size': self.last_requested_size,
            'last_screenshot_info': self.last_screenshot_info
        }
    
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
            
        Returns:
            Path to the saved screenshot file
        """
        try:
            # Store viewport information
            await self._store_viewport_info(dimensions)
            
            # Convert filepath to Path object
            filepath = Path(filepath)
            
            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Set default values
            quality = quality if quality is not None else self.default_quality
            format = format if format is not None else self.default_format
            
            # Validate quality for JPEG
            if format.lower() == 'jpeg' and not 1 <= quality <= 100:
                raise ValueError("Quality must be between 1 and 100 for JPEG format")
            
            # Resize page if dimensions provided
            original_viewport = None
            if dimensions:
                width, height = dimensions
                original_viewport = self.page.viewport_size
                await self.page.set_viewport_size({"width": width, "height": height})
                logger.info(f"Resized page to {width}x{height}")
            
            # Prepare screenshot options
            screenshot_options = {
                "path": str(filepath),
                "full_page": full_page,
                "omit_background": omit_background
            }
            
            # Add format-specific options
            if format.lower() == 'jpeg':
                screenshot_options["quality"] = quality
                screenshot_options["type"] = "jpeg"
            elif format.lower() == 'png':
                screenshot_options["type"] = "png"
            elif format.lower() == 'webp':
                screenshot_options["type"] = "webp"
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # Add clip if provided
            if clip:
                screenshot_options["clip"] = clip
            
            # Take screenshot
            logger.info(f"Taking screenshot: {filepath}")
            img_bytes: bytes = await self.page.screenshot(**screenshot_options)
            
            # Store screenshot information
            self.last_screenshot_info = {
                'filepath': str(filepath),
                'dimensions': dimensions,
                'format': format,
                'quality': quality,
                'full_page': full_page,
                'clip': clip
            }
            
            # Restore original viewport if we changed it
            if original_viewport:
                await self.page.set_viewport_size(original_viewport)
                logger.info("Restored original viewport size")
            
            logger.info(f"Screenshot saved: {filepath}")
            if return_base64:
                b64 = base64.b64encode(img_bytes).decode("ascii")
                mime = f"image/{format}"
                return f"data:{mime};base64,{b64}"
            else:
                return str(filepath)
                
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            # Check if page is still valid after error
            if self.page and not self.page.is_closed():
                logger.info("Page is still valid after screenshot error")
            else:
                logger.error("Page was closed during screenshot operation")
            raise
