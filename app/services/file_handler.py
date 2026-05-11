"""
File handler service for managing uploaded files.
Handles validation, storage, and file operations.
"""

import os
import shutil
from pathlib import Path
from typing import Optional
from uuid import uuid4


ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class FileHandlerError(Exception):
    """Custom exception for file handling errors."""
    pass


def get_upload_dir() -> Path:
    """Get the uploads directory path."""
    base_dir = Path(__file__).parent.parent.parent
    upload_dir = base_dir / "uploads"
    upload_dir.mkdir(exist_ok=True)
    return upload_dir


def validate_file_extension(filename: str) -> bool:
    """
    Validate if the file extension is allowed.
    
    Args:
        filename: The filename to validate
        
    Returns:
        True if valid, False otherwise
    """
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def validate_file_size(file_size: int) -> bool:
    """
    Validate if the file size is within limits.
    
    Args:
        file_size: Size of the file in bytes
        
    Returns:
        True if valid, False otherwise
    """
    return file_size <= MAX_FILE_SIZE


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename to avoid collisions.
    
    Args:
        original_filename: The original filename
        
    Returns:
        A unique filename with UUID prefix
    """
    ext = Path(original_filename).suffix.lower()
    unique_id = str(uuid4())[:8]
    return f"{unique_id}{ext}"


async def save_uploaded_file(file_content: bytes, original_filename: str) -> str:
    """
    Save an uploaded file to the uploads directory.
    
    Args:
        file_content: The file content as bytes
        original_filename: The original filename
        
    Returns:
        The path to the saved file
        
    Raises:
        FileHandlerError: If validation fails
    """
    # Validate file extension
    if not validate_file_extension(original_filename):
        raise FileHandlerError(
            f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    if not validate_file_size(len(file_content)):
        raise FileHandlerError(
            f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    unique_filename = generate_unique_filename(original_filename)
    upload_dir = get_upload_dir()
    file_path = upload_dir / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
        return str(file_path)
    except IOError as e:
        raise FileHandlerError(f"Failed to save file: {str(e)}")


def cleanup_file(file_path: str) -> None:
    """
    Delete a file from the uploads directory.
    
    Args:
        file_path: Path to the file to delete
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        print(f"Warning: Failed to cleanup file {file_path}: {str(e)}")


def is_pdf(file_path: str) -> bool:
    """Check if a file is a PDF."""
    return file_path.lower().endswith(".pdf")


def is_image(file_path: str) -> bool:
    """Check if a file is an image."""
    return file_path.lower().endswith((".png", ".jpg", ".jpeg"))
