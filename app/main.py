"""Invoice OCR Web Application - Main FastAPI application."""

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .services.file_handler import (
    save_uploaded_file,
    validate_file_extension,
    cleanup_file,
    FileHandlerError,
)
from .services.ai_parser import extract_invoice_data, validate_extracted_data, AIParserError


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
        # Validate file extension
        if not validate_file_extension(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: PDF, PNG, JPG, JPEG"
            )
        
        # Read file content
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty or corrupted"
            )
        
        # Save uploaded file
        try:
            file_path = await save_uploaded_file(file_content, file.filename)
        except FileHandlerError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Extract invoice data using free OCR
        try:
            extracted_data = extract_invoice_data(file_content)
        except AIParserError as e:
            error_msg = str(e)
            # Provide helpful error messages
            if "Could not find a backend" in error_msg or "No module" in error_msg:
                error_msg = "Failed to extract text from the document. Please ensure it's a valid invoice."
            
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
                        "line_items": []
                    },
                    "error": f"Extraction failed: {error_msg}"
                }
            )
        
        # Validate extracted data
        if not validate_extracted_data(extracted_data):
            raise HTTPException(
                status_code=500,
                detail="Invalid response format from extraction engine"
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
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


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
