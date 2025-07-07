"""Simple screen capture functionality."""

import base64
import io
from typing import Dict
from PIL import Image
import pyautogui


def take_screenshot(quality: int = 60) -> bytes:
    """Take a screenshot and return as base64 data URL."""
    pyautogui.FAILSAFE = False
    screenshot = pyautogui.screenshot()
    
    # Convert to base64
    buffer = io.BytesIO()
    if screenshot.mode != 'RGB':
        screenshot = screenshot.convert('RGB')
    
    # Resize while preserving aspect ratio to avoid distortion
    width, height = screenshot.size
    max_width = 1280
    
    print(f"Original size: {width}x{height}")
    
    # Only resize if too wide, preserve aspect ratio
    if width > max_width:
        ratio = max_width / width
        new_height = int(height * ratio)
        screenshot = screenshot.resize((max_width, new_height), Image.Resampling.LANCZOS)
        print(f"Resized to: {max_width}x{new_height}")
    
    screenshot.save(buffer, format='JPEG', quality=quality)
    buffer.seek(0)
    
    # Debug: Check what we're actually sending
    image_bytes = buffer.getvalue()
    print(f"Image size: {len(image_bytes)} bytes")
    print(f"JPEG header: {image_bytes[:20].hex()}")
    
    print(f"Returning {len(image_bytes)} bytes of image data")
    
    return image_bytes


def take_region_screenshot(x: int, y: int, width: int, height: int, quality: int = 85) -> bytes:
    """Take a screenshot of specific region."""
    pyautogui.FAILSAFE = False
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    
    buffer = io.BytesIO()
    if screenshot.mode != 'RGB':
        screenshot = screenshot.convert('RGB')
    
    screenshot.save(buffer, format='JPEG', quality=quality)
    buffer.seek(0)
    return buffer.getvalue()


def get_screen_size() -> Dict[str, int]:
    """Get screen dimensions."""
    size = pyautogui.size()
    return {"width": size.width, "height": size.height}


def get_cursor_position() -> Dict[str, int]:
    """Get mouse cursor position."""
    x, y = pyautogui.position()
    return {"x": x, "y": y}