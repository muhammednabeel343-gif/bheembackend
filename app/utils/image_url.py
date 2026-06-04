"""
Utility functions for handling image URLs dynamically.
Rewrites hardcoded localhost URLs to current deployment URL.
"""
from urllib.parse import urlparse
from app.config import settings


def normalize_image_url(image_url: str | None) -> str | None:
    """
    Normalize image URLs to use current API_BASE_URL.
    
    Handles:
    - Hardcoded localhost URLs (http://127.0.0.1:8000)
    - Old development URLs
    - Already correct URLs
    
    Args:
        image_url: Image URL from database (may be hardcoded localhost)
        
    Returns:
        Corrected URL using current API_BASE_URL, or None if no image
    """
    if not image_url:
        return None
    
    # Extract just the filename/path if it's a full URL
    if image_url.startswith("http://") or image_url.startswith("https://"):
        try:
            parsed = urlparse(image_url)
            # Extract path after /uploads/
            path_parts = parsed.path.split("/uploads/")
            if len(path_parts) > 1:
                filename = path_parts[1]
            else:
                # Fallback to path as-is
                filename = parsed.path.lstrip("/")
        except Exception:
            # If parsing fails, return original
            return image_url
    else:
        # Already relative path
        filename = image_url.lstrip("/")
    
    # Reconstruct with current API_BASE_URL
    if settings.api_base_url:
        return f"{settings.api_base_url}/uploads/{filename}"
    else:
        # Fallback: return relative path
        return f"/uploads/{filename}"
