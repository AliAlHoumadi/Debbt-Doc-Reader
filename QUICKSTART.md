# Quick Start Guide 🚀

Get the Invoice OCR Scanner running in 2 minutes!

## Step 1: Install Dependencies 📦

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Note for Windows:** If you see errors with pdf2image, run:
```bash
choco install poppler
```

## Step 2: Run Development Mode 🎯

```bash
python dev.py
```

This will:
- 📝 Ask for your OpenAI API key
- 💾 Save it securely to `.env`
- 🚀 Start development server with auto-reload

## Step 3: Get Your API Key 🔑

You'll be prompted for your OpenAI API key. Get one here:
- Go to: https://platform.openai.com/api-keys
- Sign in to your account
- Click "Create new secret key"
- Copy the key (starts with `sk-`)
- Paste it into the prompt

## Step 4: Open in Browser 🌐

The server will start at: **http://localhost:8000**

1. Upload an invoice (PDF, PNG, JPG)
2. Wait for processing
3. View extracted data
4. Download or copy JSON!

## 📝 What Gets Extracted

- Supplier company name
- Customer/debtor name
- Invoice number & date
- Payment terms
- Subtotal, tax, total amount
- IBAN (if available)
- Line items with quantities and prices

## 📊 That's It!

You're ready to use the application. The development mode:
- ✅ Handles API key interactive setup
- ✅ Auto-reloads on code changes
- ✅ Shows detailed logs
- ✅ Keeps things clean

## ❓ Need Help?

- **API key issues**: Make sure it starts with `sk-`
- **Port in use**: App uses port 8000 by default
- **PDF errors**: Check if poppler is installed (Windows)
- **See full README**: Run `cat README.md`

## 🎉 Start Scanning!

```bash
python dev.py
```

Then open http://localhost:8000 in your browser.

---

**Tip**: Keep the `python dev.py` terminal running while using the app.

