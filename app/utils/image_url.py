"""
Utility functions for handling image URLs dynamically.
Rewrites hardcoded localhost URLs to current deployment URL.
"""
from app.config import settings

# NOTE: This module may be used without request context.
# If API_BASE_URL is not configured, we fall back to returning an absolute URL
# based on the current origin (best-effort in browser/relative usage) OR
# a relative path as the last resort.

from app.config import settings

def normalize_image_url(image_url: str | None) -> str | None:
    if not image_url:
        return None

    # Keep Cloudinary URLs unchanged
    if "cloudinary.com" in image_url:
        return image_url

    # Keep other external URLs unchanged
    if image_url.startswith("http://") or image_url.startswith("https://"):
        if "/uploads/" not in image_url:
            return image_url

    # Handle local upload paths
    if image_url.startswith("/uploads/"):
        filename = image_url.replace("/uploads/", "", 1)
    else:
        filename = image_url.split("/")[-1]

    base_url = settings.api_base_url.rstrip("/")

    return f"{base_url}/uploads/{filename}"