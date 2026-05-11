"""
Invoice OCR Web Application
Main FastAPI application for invoice scanning and data extraction.
"""

import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
import traceback

from .services.file_handler import (
    save_uploaded_file,
    validate_file_extension,
    cleanup_file,
    FileHandlerError,
)
from .services.ai_parser import extract_invoice_data, validate_extracted_data, AIParserError


# Global API key storage (session-based, not persisted)
_api_key_store = {}


class APIKeyRequest(BaseModel):
    """Request model for API key submission."""
    apiKey: str


def get_api_key() -> str:
    """Get API key from environment or session store."""
    # Check session store first
    if _api_key_store.get("key"):
        return _api_key_store["key"]
    
    # Check environment variables
    return os.environ.get("OPENAI_API_KEY", "").strip()


def has_api_key() -> bool:
    """Check if API key is available."""
    return bool(get_api_key())


# Initialize FastAPI app
app = FastAPI(
    title="Invoice OCR Scanner",
    description="Extract structured data from invoices using AI",
    version="1.0.0"
)

# Setup template and static directories
app_dir = Path(__file__).parent
templates = Jinja2Templates(directory=str(app_dir / "templates"))
static_dir = app_dir / "static"
static_dir.mkdir(exist_ok=True)

# Mount static files
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/setup", response_class=HTMLResponse)
async def setup(request: Request):
    """
    Serve the API key setup page.
    """
    return templates.TemplateResponse("setup.html", {"request": request})


@app.post("/api/set-api-key")
async def set_api_key(request: APIKeyRequest):
    """
    Accept and store API key for the session.
    """
    if not request.apiKey:
        raise HTTPException(status_code=400, detail="API key is required")
    
    if not request.apiKey.startswith("sk-"):
        raise HTTPException(status_code=400, detail="Invalid API key format")
    
    # Store in session store
    _api_key_store["key"] = request.apiKey.strip()
    
    return JSONResponse(
        status_code=200,
        content={"success": True, "message": "API key set successfully"}
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Serve the main upload page.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/upload")
async def upload_invoice(file: UploadFile = File(...)):
    """
    Handle invoice file upload and extraction.
    
    Args:
        file: Uploaded invoice file (PDF, PNG, JPG, or JPEG)
        
    Returns:
        JSON response with extracted invoice data or error
    """
    file_path = None
    
    try:
        # No API key needed - using free OCR
        
        # Validate file extension
        if not validate_file_extension(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.filename}. Allowed: PNG, JPG, JPEG"
            )
        
        # Read file content
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )
        
        # Save uploaded file
        try:
            file_path = await save_uploaded_file(file_content, file.filename)
        except FileHandlerError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Extract invoice data using free OCR (works with PDF and images)
        try:
            extracted_data = extract_invoice_data(file_content)
        except AIParserError as e:
            print(f"DEBUG: Extraction error: {str(e)}")
            # Return a simple message if extraction fails
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": {
                        "supplier": "No data found",
                        "customer": "No data found",
                        "invoice_number": "No data found",
                        "invoice_date": "No data found",
                        "payment_term": "No data found",
                        "subtotal": "No data found",
                        "tax_vat": "No data found",
                        "total_amount": "No data found",
                        "iban": None,
                        "line_items": [],
                        "message": f"Error: {str(e)}"
                    }
                }
            )
        
        # Validate extracted data
        if not validate_extracted_data(extracted_data):
            raise HTTPException(
                status_code=500,
                detail="Invalid response format from AI"
            )
        
        # Clean up uploaded file
        cleanup_file(file_path)
        file_path = None
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": extracted_data
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    finally:
        # Ensure file cleanup on error
        if file_path:
            cleanup_file(file_path)


@app.get("/result", response_class=HTMLResponse)
async def result_page(request: Request):
    """
    Serve the results page template.
    """
    return templates.TemplateResponse("result.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
