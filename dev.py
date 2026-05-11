"""
Development Mode Entry Point
Starts the development server with auto-reload.

Usage:
    python dev.py

Then open http://localhost:8000 in your browser.
The setup page will guide you to enter your OpenAI API key.
"""

import sys
import uvicorn


def main():
    """Start the development server."""
    print("\n" + "=" * 60)
    print("🚀 Invoice OCR Scanner - Development Mode")
    print("=" * 60)
    print("\n📍 Server starting at: http://localhost:8000")
    print("🔄 Auto-reload enabled")
    print("🛑 Press Ctrl+C to stop\n")
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n✋ Development server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✋ Setup cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

