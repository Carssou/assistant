"""
Tools for the PydanticAI agent.

This module contains tool definitions that will be registered with the agent.
"""

import time
import base64
from pathlib import Path
from typing import Dict, Any

from pydantic_ai import RunContext
from pydantic_ai.agent import Agent

from agent.dependencies import AgentDependencies
from utils.screen_capture import get_screenshot_capture


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


def register_tools(agent: Agent[AgentDependencies]) -> None:
    """
    Register all tools with the PydanticAI agent.
    
    Args:
        agent: The PydanticAI agent instance to register tools with
    """
    
    @agent.tool
    def take_screenshot(ctx: RunContext[AgentDependencies], quality: int = 75) -> str:
        """
        Take a screenshot for analysis.
        
        Args:
            quality: Image quality (1-100, default 75)
            
        Returns:
            Base64 encoded image data URL
        """
        try:
            # Get model-optimized quality
            config = ctx.deps.config
            model_name = config.llm_choice.lower()
            
            # Adjust quality for small models
            small_model_keywords = ['lite', 'micro', 'mini']
            if any(keyword in model_name for keyword in small_model_keywords):
                quality = max(15, quality // 3)
            
            # Take screenshot
            capture = get_screenshot_capture()
            result = capture.take_screenshot(quality)
            
            # Save for user transparency
            _save_screenshot(result, "screenshot")
            
            return result
        except Exception as e:
            return f"Error taking screenshot: {str(e)}"
    
    @agent.tool
    def take_region_screenshot(ctx: RunContext[AgentDependencies], x: int, y: int, width: int, height: int, quality: int = 85) -> str:
        """
        Take a screenshot of a specific screen region.
        
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
    
    @agent.tool
    def get_screen_info(ctx: RunContext[AgentDependencies]) -> Dict[str, Any]:
        """
        Get information about the current screen/desktop.
        
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