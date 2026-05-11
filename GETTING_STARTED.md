# Getting Started 🚀

## The Easiest Way

Just run this command:

```bash
python dev.py
```

That's it! It will:
- Ask for your OpenAI API key (paste it when prompted)
- Save it automatically
- Start the development server
- Open http://localhost:8000

## Prerequisites

1. **Python 3.11+** - Download from https://python.org
2. **OpenAI API Key** - Get from https://platform.openai.com/api-keys

## Installation (One Time)

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate    # macOS/Linux
# or
venv\Scripts\activate       # Windows

# 2. Install dependencies
pip install -r requirements.txt
```

## Running the App

```bash
python dev.py
```

When asked for your API key:
1. Go to https://platform.openai.com/api-keys
2. Copy your key (starts with `sk-`)
3. Paste it into the prompt
4. Press Enter
5. Server starts automatically!

Then open: **http://localhost:8000**

## That's All!

Upload a PDF or image of an invoice and the AI will extract all the data for you.

## Tips

- **First run**: Will ask for API key
- **Next runs**: Uses saved key (press Enter to skip, or type 'y' to update)
- **Development mode**: Auto-reloads when you edit code
- **Stop server**: Press Ctrl+C in terminal

## Need Help?

- See `README.md` for detailed documentation
- See `QUICKSTART.md` for common questions
- Check error messages in the terminal

---

**That's it! Happy scanning!** 📧✨
