"""
Utility functions for handling image URLs dynamically.
Rewrites hardcoded localhost URLs to current deployment URL.
"""
from urllib.parse import urlparse
from app.config import settings

# NOTE: This module may be used without request context.
# If API_BASE_URL is not configured, we fall back to returning an absolute URL
# based on the current origin (best-effort in browser/relative usage) OR
# a relative path as the last resort.



def normalize_image_url(image_url: str | None) -> str | None:
    """
    Normalize image URLs to use current API_BASE_URL.
    
    Handles:
    - Hardcoded localhost URLs (http://127.0.0.1:8000)
    - Old development URLs (http://localhost:8000)
    - Relative paths (/uploads/filename.jpg)
    - Just filenames (filename.jpg)
    - Any domain with /uploads/ path
    
    Args:
        image_url: Image URL from database (may be hardcoded localhost, relative, or full URL)
        
    Returns:
        Corrected URL using current API_BASE_URL, or None if no image
    """
    if not image_url:
        return None
    
    # If it's already a relative path, just return it as-is
    if image_url.startswith("/uploads/"):
        filename = image_url.replace("/uploads/", "", 1)
    # If it's a full URL, extract the filename
    elif image_url.startswith("http://") or image_url.startswith("https://"):
        try:
            parsed = urlparse(image_url)
            # Extract filename from path
            if "/uploads/" in parsed.path:
                filename = parsed.path.split("/uploads/", 1)[1]
            else:
                # Path doesn't have /uploads/, use the last segment
                filename = parsed.path.split("/")[-1]
        except Exception:
            # If parsing fails, treat as relative
            filename = image_url.lstrip("/")
    else:
        # Just a filename
        filename = image_url
    
    # Ensure filename is clean (no empty strings)
    if not filename:
        return None
    
    # Get the base URL, removing any trailing slashes
    base_url = settings.api_base_url
    if base_url:
        base_url = base_url.rstrip("/")
        return f"{base_url}/uploads/{filename}"

    # Fallback when API_BASE_URL is missing:
    # Keep the /uploads/* prefix so the frontend can prefix it with VITE_API_BASE_URL
    # (or serve relative to the current origin).
    return f"/uploads/{filename}"
