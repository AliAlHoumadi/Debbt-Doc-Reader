# Invoice OCR Scanner 🧾

Extract invoice data from invoices instantly - **completely free, no API key needed!**

## Setup & Run

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
source venv/Scripts/activate          # macOS/Linux/Git Bash
# or for CMD on Windows:
# venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python dev.py
```

Then open: **http://localhost:8000**

Upload your invoice (PDF, PNG, JPG, JPEG) and extract data instantly!

there is a test file u can use in the /testDoc folder.


**Supported formats:** PDF, PNG, JPG, JPEG

---

**Made with FastAPI + PaddleOCR (Free & Offline) + TailwindCSS**

**Features:**
- ✅ 100% free - no API keys required
- ✅ Works offline - everything runs locally
- ✅ Supports multiple formats: PDF, PNG, JPG, JPEG
- ✅ Extracts: Supplier, Customer, Invoice Number, Date, Amounts, Line Items, IBAN
