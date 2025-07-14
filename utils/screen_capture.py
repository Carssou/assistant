"""Simple screen capture functionality."""

import io

import pyautogui
from PIL import Image


def take_screenshot(quality: int = 60) -> bytes:
    """
    Take a screenshot and return as raw image bytes.
    
    Args:
        quality: JPEG quality (1-100, default 60). Higher values produce better quality but larger files.
        
    Returns:
        Raw JPEG image bytes of the screenshot.
    """
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
    """
    Take a screenshot of a specific rectangular region.
    
    Args:
        x: Left coordinate of the region in pixels.
        y: Top coordinate of the region in pixels.
        width: Width of the region in pixels.
        height: Height of the region in pixels.
        quality: JPEG quality (1-100, default 85). Higher values produce better quality but larger files.
        
    Returns:
        Raw JPEG image bytes of the specified region.
    """
    pyautogui.FAILSAFE = False
    screenshot = pyautogui.screenshot(region=(x, y, width, height))

    buffer = io.BytesIO()
    if screenshot.mode != 'RGB':
        screenshot = screenshot.convert('RGB')

    screenshot.save(buffer, format='JPEG', quality=quality)
    buffer.seek(0)
    return buffer.getvalue()


def get_screen_size() -> dict[str, int]:
    """
    Get the current screen dimensions.
    
    Returns:
        Dictionary containing screen width and height in pixels.
        Format: {"width": int, "height": int}
    """
    size = pyautogui.size()
    return {"width": size.width, "height": size.height}


def get_cursor_position() -> dict[str, int]:
    """
    Get the current mouse cursor position.
    
    Returns:
        Dictionary containing cursor x and y coordinates in pixels.
        Format: {"x": int, "y": int}
    """
    x, y = pyautogui.position()
    return {"x": x, "y": y}
