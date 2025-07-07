"""
Tools for the PydanticAI agent.

This module contains the actual tool implementation functions that will be 
imported and wrapped with @agent.tool decorators in agent.py.
Following PydanticAI patterns from the reference implementation.
"""

import time
import base64
from pathlib import Path
from typing import Dict, Any

from pydantic_ai import BinaryContent
from agent.dependencies import AgentDependencies
from utils.screen_capture import take_screenshot, take_region_screenshot, get_screen_size, get_cursor_position


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
    """
    try:
        image_bytes = take_region_screenshot(x, y, width, height, quality)
        return BinaryContent(data=image_bytes, media_type="image/jpeg")
    except Exception as e:
        raise RuntimeError(f"Error taking region screenshot: {str(e)}")


async def get_screen_info_tool(deps: AgentDependencies) -> Dict[str, Any]:
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


# Legacy functions for backward compatibility (if needed elsewhere)
def _get_model_optimized_quality(base_quality: int) -> int:
    """Adjust image quality based on model capabilities."""
    try:
        from config.settings import load_config
        config = load_config()
        model_name = config.llm_choice.lower()
        
        # Check for small models that need lower quality
        small_model_keywords = ['lite', 'micro', 'mini']
        if any(keyword in model_name for keyword in small_model_keywords):
            # Reduce quality significantly for small models
            return max(15, base_quality // 3)  # Minimum 15, or 1/3 of base quality
        
        return base_quality
    except Exception:
        return base_quality


def take_screenshot_legacy(quality: int = 75) -> str:
    """
    Legacy screenshot function - use agent tools instead.
    
    Args:
        quality: Image quality (1-100, default 75)
        
    Returns:
        Base64 encoded image data URL
    """
    try:
        # Optimize quality for model capabilities
        optimized_quality = _get_model_optimized_quality(quality)
        
        # Take ONE screenshot
        capture = get_screenshot_capture()
        result = capture.take_screenshot(optimized_quality)
        
        # Debug: Log data URL start for verification
        data_preview = result[:100] if len(result) > 100 else result
        print(f"🔍 Screenshot data starts with: {data_preview}")
        
        # Save SAME data for user transparency
        saved_path = _save_screenshot(result, "screenshot")
        if saved_path:
            print(f"📸 Screenshot saved: {saved_path} (quality: {optimized_quality})")
            print(f"✅ Agent and user seeing IDENTICAL screenshot")
        
        return result
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"


def take_region_screenshot_legacy(x: int, y: int, width: int, height: int, quality: int = 85) -> str:
    """
    Legacy region screenshot function - use agent tools instead.
    
    Args:
        x: Left coordinate of region
        y: Top coordinate of region  
        width: Width of region
        height: Height of region
        quality: Image quality (1-100, default 85)
        
    Returns:
        Base64 encoded PNG image data URL
    """
    try:
        capture = get_screenshot_capture()
        return capture.take_region_screenshot(x, y, width, height, quality)
    except Exception as e:
        return f"Error taking region screenshot: {str(e)}"


def get_screen_info_legacy() -> Dict[str, Any]:
    """
    Legacy screen info function - use agent tools instead.
    
    Returns:
        Dictionary with screen dimensions and cursor position
    """
    try:
        capture = get_screenshot_capture()
        screen_size = capture.get_screen_size()
        cursor_pos = capture.get_cursor_position()
        
        return {
            "screen_size": screen_size,
            "cursor_position": cursor_pos,
            "timestamp": time.time()
        }
    except Exception as e:
        return {"error": f"Error getting screen info: {str(e)}"}