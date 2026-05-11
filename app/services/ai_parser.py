"""Invoice parser service using free, open-source EasyOCR."""

import re
from typing import Dict, Any
import easyocr
import fitz
import tempfile


class AIParserError(Exception):
    """Custom exception for parsing errors."""
    pass


# Initialize OCR once (reuse for performance)
_reader = None

def get_ocr_reader():
    """Get or initialize OCR reader with multiple languages."""
    global _reader
    if _reader is None:
        # Support multiple European languages for invoice processing
        _reader = easyocr.Reader(['en', 'es', 'fr', 'de', 'nl', 'it', 'pt'], gpu=False)
    return _reader


def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extract text from image or PDF bytes using EasyOCR.
    
    Args:
        image_bytes: Raw image or PDF bytes
        
    Returns:
        Extracted text
        
    Raises:
        AIParserError: If extraction fails
    """
    try:
        # Detect file type from magic bytes
        is_pdf = image_bytes.startswith(b'%PDF')
        
        reader = get_ocr_reader()
        full_text = ""
        
        if is_pdf:
            print("DEBUG: Converting PDF to images...")
            # Convert PDF pages to images
            pdf_doc = fitz.open(stream=image_bytes, filetype="pdf")
            for page_num, page in enumerate(pdf_doc):
                print(f"DEBUG: Processing PDF page {page_num + 1}/{len(pdf_doc)}")
                # Render page to image (mat = matrix for zoom)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
                img_data = pix.tobytes("ppm")
                
                # Run OCR on this page
                result = reader.readtext(img_data, detail=0)
                full_text += "\n".join(result) + "\n---PAGE BREAK---\n"
            pdf_doc.close()
        else:
            print("DEBUG: Processing image file...")
            # Save image to temp file and run OCR
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp.write(image_bytes)
                temp_path = tmp.name
            
            result = reader.readtext(temp_path, detail=0)
            full_text = "\n".join(result)
        
        print(f"DEBUG: Extracted text length: {len(full_text)}")
        return full_text
    
    except Exception as e:
        raise AIParserError(f"Failed to extract text from image: {str(e)}")


def parse_invoice_fields(text: str) -> Dict[str, Any]:
    """
    Parse invoice fields from extracted text using regex patterns.
    
    Args:
        text: Extracted text from invoice
        
    Returns:
        Dictionary with parsed invoice data
    """
    
    # Helper function to search for patterns
    def search_pattern(patterns, text):
        """Search for value after various keywords."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return match.group(1).strip()
                except:
                    return match.group(0).strip()
        return None
    
    # Helper to find currency amounts
    def find_amount(pattern, text):
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            last_match = matches[-1]
            # Handle case where regex has multiple groups (returns tuples)
            if isinstance(last_match, tuple):
                # Get first non-empty value from tuple
                for item in last_match:
                    if item:
                        return item.strip()
            else:
                return last_match.strip()
        return None
    
    # Extract fields (multilingual patterns)
    data = {
        # Supplier: Look for multiple keyword variations
        "supplier": search_pattern([
            r"(?:supplier|from|issued by|empresa|fournisseur|lieferant|leverancier|fornitore|fornecedor)[:\s]+([^\n]+)",
            r"(?:proveedor|fournisseur|anbieter)[:\s]+([^\n]+)",
        ], text) or "Unknown",
        
        # Customer: Bill to, send to, etc. in multiple languages
        "customer": search_pattern([
            r"(?:customer|to|bill to|cliente|client|facturer à|kunde|klant|cliente)[:\s]+([^\n]+)",
        ], text) or "Unknown",
        
        # Invoice number: Usually alphanumeric, language-independent
        "invoice_number": search_pattern([
            r"(?:invoice\s+(?:number|no|#)|factura|rechnung|número|num|no)[:\s#]*([A-Z0-9\-\/]+)",
            r"(?:inv|ref|rfc)[:\s]*([A-Z0-9\-\/]+)",
        ], text) or None,
        
        # Invoice date: Accept multiple date formats
        "invoice_date": search_pattern([
            r"(?:invoice\s+date|date|fecha|date\s+de|datum)[:\s]*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})",
            r"(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})",
        ], text) or None,
        
        # Payment term: Days or due date info
        "payment_term": search_pattern([
            r"(?:payment\s+(?:term|terms)|plazo|délai|bedingung|betaling|termine)[:\s]*([^\n]+?)(?:\n|$)",
            r"(?:due|vencimiento|échéance|fällig)[:\s]*([^\n]+?)(?:\n|$)",
            r"(net\s+\d+|\d+\s+(?:days|días|jours|tage|dagen|giorni|dias))",
        ], text) or None,
        
        # IBAN: International format, same everywhere
        "iban": search_pattern([
            r"(?:iban)[:\s]*([A-Z]{2}[0-9A-Z]{1,30})",
        ], text) or None,
        
        # Subtotal: Any currency symbol followed by amount
        "subtotal": find_amount(r"(?:subtotal|sub.total|subtotales|sous.total|zwischensumme|subtotaal)[:\s]*([\d,\.€$£]+(?:[,\.]\d{2})?)", text) or None,
        
        # Tax/VAT: Works in most languages
        "tax_vat": find_amount(r"(?:vat|tax|iva|tva|mwst|btw|iva|imposto)[:\s]*\(.*?\)\s*([\d,\.€$£]+(?:[,\.]\d{2})?)|(?:vat|tax|iva|tva|mwst|btw)[:\s]*([\d,\.€$£]+(?:[,\.]\d{2})?)", text) or None,
        
        # Total amount: Most important, look for multiple keywords
        "total_amount": find_amount(r"(?:total\s+(?:amount|due|a payer)|monto\s+total|montant\s+total|gesamtbetrag|totaal|totale)[:\s]*([\d,\.€$£]+(?:[,\.]\d{2})?)", text) or find_amount(r"(?:total)[:\s]*([\d,\.€$£]+(?:[,\.]\d{2})?)", text) or None,
    }
    
    # Line items removed
    data["line_items"] = []
    
    return data


def extract_invoice_data(image_bytes: bytes, api_key: str = None) -> Dict[str, Any]:
    """
    Extract invoice data from an image using EasyOCR.
    
    Args:
        image_bytes: Image bytes to analyze
        api_key: Ignored (included for API compatibility)
        
    Returns:
        Dictionary containing extracted invoice data
        
    Raises:
        AIParserError: If extraction fails
    """
    try:
        # Extract text from image
        text = extract_text_from_image(image_bytes)
        
        # Parse fields from text
        extracted_data = parse_invoice_fields(text)
        
        return extracted_data
    
    except AIParserError:
        raise
    except Exception as e:
        raise AIParserError(f"Failed to extract invoice data: {str(e)}")


def validate_extracted_data(data: Dict[str, Any]) -> bool:
    """
    Validate that the extracted data has the expected structure.
    
    Args:
        data: The extracted data dictionary
        
    Returns:
        True if valid, False otherwise
    """
    # Basic validation - just check if it's a dictionary with expected keys
    required_keys = [
        "supplier",
        "customer", 
        "invoice_number",
        "invoice_date",
        "payment_term",
        "subtotal",
        "tax_vat",
        "total_amount",
        "iban",
        "line_items"
    ]
    
    if not isinstance(data, dict):
        return False
    
    # All keys should be present (but can be None)
    for key in required_keys:
        if key not in data:
            return False
    
    # line_items should be a list
    if not isinstance(data.get("line_items"), list):
        return False
    
    return True

