"""Screen capture functionality for the productivity agent."""

import base64
import io
import time
from typing import Dict, Any, Optional
from PIL import Image
import pyautogui


class ScreenshotCapture:
    """Handles screenshot capture and basic image operations."""
    
    def __init__(self):
        # Disable pyautogui's fail-safe feature for server use
        pyautogui.FAILSAFE = False
        
    def get_screen_size(self) -> Dict[str, int]:
        """Get screen dimensions."""
        size = pyautogui.size()
        return {"width": size.width, "height": size.height}
    
    def take_screenshot(self, quality: int = 85) -> str:
        """Take a full screenshot and return as base64 encoded PNG."""
        screenshot = pyautogui.screenshot()
        
        # Debug: Print image info
        print(f"🖼️  Screenshot captured: {screenshot.size} mode: {screenshot.mode}")
        
        # Ensure proper orientation (don't auto-rotate)
        # Some systems may have EXIF rotation data that we want to preserve
        
        return self._image_to_base64(screenshot, quality)
    
    def take_region_screenshot(self, x: int, y: int, width: int, height: int,
                              quality: int = 85) -> str:
        """Take a screenshot of a specific region."""
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return self._image_to_base64(screenshot, quality)
    
    def get_cursor_position(self) -> Dict[str, int]:
        """Get current mouse cursor position."""
        x, y = pyautogui.position()
        return {"x": x, "y": y}
    
    def _image_to_base64(self, image: Image.Image, quality: int = 85) -> str:
        """Convert PIL Image to base64 encoded string with smart format selection."""
        buffer = io.BytesIO()
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize ALL images by 75% to keep under 1.2MB for both Lite and Pro
        width, height = image.size
        new_width = int(width * 0.75)  # 75% of original size
        new_height = int(height * 0.75)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Use JPEG for better compression
        image.save(buffer, format='JPEG', quality=quality, optimize=True)
        format_prefix = "data:image/jpeg;base64,"
        
        buffer.seek(0)
        encoded_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"{format_prefix}{encoded_string}"


# Global instance for tools to use
_screenshot_capture = None


def get_screenshot_capture() -> ScreenshotCapture:
    """Get or create the global screenshot capture instance."""
    global _screenshot_capture
    if _screenshot_capture is None:
        _screenshot_capture = ScreenshotCapture()
    return _screenshot_capture