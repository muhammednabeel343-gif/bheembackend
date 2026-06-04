"""Cloudinary image upload service."""

import cloudinary
import cloudinary.uploader
from typing import Optional
from app.config import settings


def initialize_cloudinary():
    """Initialize Cloudinary with credentials from settings."""
    if settings.cloudinary_cloud_name and settings.cloudinary_api_key and settings.cloudinary_api_secret:
        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
        )
        return True
    return False


def upload_image(file_data: bytes, filename: str, folder: str = "game-thumbnails") -> Optional[str]:
    """
    Upload image to Cloudinary.
    
    Args:
        file_data: Image file bytes
        filename: Original filename
        folder: Cloudinary folder path (default: game-thumbnails)
    
    Returns:
        Cloudinary image URL or None if upload fails
    """
    try:
        if not settings.cloudinary_cloud_name:
            return None
        
        # Remove extension and use as public_id
        public_id = filename.rsplit(".", 1)[0] if "." in filename else filename
        
        result = cloudinary.uploader.upload(
            file_data,
            folder=folder,
            public_id=public_id,
            overwrite=True,
            resource_type="auto",
        )
        
        return result.get("secure_url")  # Returns HTTPS URL
    
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        return None


def delete_image(public_id: str) -> bool:
    """
    Delete image from Cloudinary.
    
    Args:
        public_id: Cloudinary public ID (without folder prefix)
    
    Returns:
        True if deletion succeeded, False otherwise
    """
    try:
        if not settings.cloudinary_cloud_name:
            return False
        
        cloudinary.uploader.destroy(public_id)
        return True
    
    except Exception as e:
        print(f"Cloudinary delete error: {e}")
        return False


def get_cloudinary_url(public_id: str, transformation: Optional[dict] = None) -> Optional[str]:
    """
    Generate Cloudinary URL with optional transformations.
    
    Args:
        public_id: Cloudinary public ID
        transformation: Optional transformation dict (e.g., {"width": 300, "height": 300, "crop": "fill"})
    
    Returns:
        Cloudinary URL
    """
    if not settings.cloudinary_cloud_name:
        return None
    
    try:
        url = cloudinary.CloudinaryImage(public_id).build_url(
            transformation=transformation,
            secure=True,
        )
        return url
    except Exception as e:
        print(f"Cloudinary URL generation error: {e}")
        return None
