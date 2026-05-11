"""
PDF conversion service for converting PDF pages to images.
Uses PyMuPDF (fitz) - no external dependencies needed.
"""

from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import io


class PDFConversionError(Exception):
    """Custom exception for PDF conversion errors."""
    pass


def convert_pdf_to_image(pdf_path: str) -> bytes:
    """
    Convert the first page of a PDF to an image.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Image bytes in PNG format
        
    Raises:
        PDFConversionError: If conversion fails
    """
    try:
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(pdf_path)
        
        if len(pdf_document) == 0:
            raise PDFConversionError("PDF has no pages")
        
        # Get first page
        first_page = pdf_document[0]
        
        # Render page to image at 200 DPI (1.5x zoom for standard 72 DPI)
        pix = first_page.get_pixmap(matrix=fitz.Matrix(2, 2))
        
        # Convert to PIL Image for PNG encoding
        img_data = pix.tobytes("ppm")
        img = Image.open(io.BytesIO(img_data))
        
        # Convert to PNG bytes
        png_bytes = io.BytesIO()
        img.save(png_bytes, format="PNG")
        png_bytes.seek(0)
        
        pdf_document.close()
        return png_bytes.getvalue()
    
    except PDFConversionError:
        raise
    except Exception as e:
        raise PDFConversionError(f"Failed to convert PDF: {str(e)}")


def get_image_for_processing(file_path: str) -> bytes:
    """
    Get image bytes from either a PDF or image file.
    If PDF, converts first page to PNG.
    If image, reads directly.
    
    Args:
        file_path: Path to the PDF or image file
        
    Returns:
        Image bytes
        
    Raises:
        PDFConversionError: If file processing fails
    """
    file_path_lower = file_path.lower()
    
    if file_path_lower.endswith(".pdf"):
        return convert_pdf_to_image(file_path)
    elif file_path_lower.endswith((".png", ".jpg", ".jpeg")):
        try:
            with open(file_path, "rb") as f:
                return f.read()
        except IOError as e:
            raise PDFConversionError(f"Failed to read image file: {str(e)}")
    else:
        raise PDFConversionError("Unsupported file format")
