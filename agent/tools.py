"""
Tools for the PydanticAI agent.

This module contains the actual tool implementation functions that will be 
imported and wrapped with @agent.tool decorators in agent.py.
Following PydanticAI patterns from the reference implementation.
"""

import base64
import time
from pathlib import Path
from typing import Any

from pydantic_ai import BinaryContent

from agent.dependencies import AgentDependencies
from utils.screen_capture import (
    get_cursor_position,
    get_screen_size,
    take_region_screenshot,
    take_screenshot,
)


def _save_screenshot(data_url: str, prefix: str = "screenshot") -> str:
    """Save screenshot to screenshots folder for user transparency."""
    try:
        # Create screenshots folder
        screenshots_dir = Path("screenshots")
        screenshots_dir.mkdir(exist_ok=True)

        # Handle both PNG and JPEG formats
        if data_url.startswith("data:image/png;base64,"):
            base64_data = data_url.split(",")[1]
            extension = "png"
        elif data_url.startswith("data:image/jpeg;base64,"):
            base64_data = data_url.split(",")[1]
            extension = "jpg"
        else:
            print(f"Unknown image format in data URL: {data_url[:50]}...")
            return ""

        # Generate unique filename with microseconds to prevent overwrites
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        microseconds = int(time.time() * 1000000) % 1000000
        filename = f"{prefix}_{timestamp}_{microseconds:06d}.{extension}"
        filepath = screenshots_dir / filename

        # Save to file
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(base64_data))

        # Print file size for debugging
        file_size = filepath.stat().st_size
        print(f"📸 Screenshot saved: {filepath} ({file_size:,} bytes)")

        return str(filepath)
    except Exception as e:
        print(f"Screenshot save failed: {e}")
        return ""


async def take_screenshot_tool(deps: AgentDependencies, quality: int = 75) -> BinaryContent:
    """
    Take a screenshot for analysis.
    
    Args:
        deps: Agent dependencies containing config and other resources
        quality: Image quality (1-100, default 75)
        
    Returns:
        BinaryContent with the screenshot image
        
    Raises:
        RuntimeError: If screenshot capture fails
    """
    try:
        # Get model-optimized quality
        model_name = deps.config.llm_choice.lower()

        # Adjust quality for small models
        small_model_keywords = ['lite', 'micro', 'mini']
        if any(keyword in model_name for keyword in small_model_keywords):
            quality = max(15, quality // 3)

        # Take screenshot
        image_bytes = take_screenshot(quality)

        # Save for user transparency (convert back to data URL for saving)
        import base64
        encoded = base64.b64encode(image_bytes).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{encoded}"
        _save_screenshot(data_url, "screenshot")

        return BinaryContent(data=image_bytes, media_type="image/jpeg")
    except Exception as e:
        # For errors, we can't return BinaryContent, so raise an exception
        raise RuntimeError(f"Error taking screenshot: {str(e)}")


async def take_region_screenshot_tool(deps: AgentDependencies, x: int, y: int, width: int, height: int, quality: int = 85) -> BinaryContent:
    """
    Take a screenshot of a specific screen region.
    
    Args:
        deps: Agent dependencies
        x: Left coordinate of region
        y: Top coordinate of region  
        width: Width of region
        height: Height of region
        quality: Image quality (1-100, default 85)
        
    Returns:
        BinaryContent with the region screenshot image
        
    Raises:
        RuntimeError: If region screenshot capture fails
    """
    try:
        image_bytes = take_region_screenshot(x, y, width, height, quality)
        return BinaryContent(data=image_bytes, media_type="image/jpeg")
    except Exception as e:
        raise RuntimeError(f"Error taking region screenshot: {str(e)}")


async def get_screen_info_tool(deps: AgentDependencies) -> dict[str, Any]:
    """
    Get information about the current screen/desktop.
    
    Args:
        deps: Agent dependencies
        
    Returns:
        Dictionary with screen dimensions and cursor position
    """
    try:
        screen_size = get_screen_size()
        cursor_pos = get_cursor_position()

        return {
            "screen_size": screen_size,
            "cursor_position": cursor_pos,
            "timestamp": time.time()
        }
    except Exception as e:
        return {"error": f"Error getting screen info: {str(e)}"}


