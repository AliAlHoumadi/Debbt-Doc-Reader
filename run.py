"""
Invoice OCR Scanner - Entry Point
Run this file to start the application: python run.py
"""

import uvicorn
import sys
from pathlib import Path

# Add app to path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir.parent))

if __name__ == "__main__":
    print("=" * 60)
    print("Invoice OCR Scanner")
    print("=" * 60)
    print("\n🚀 Starting application...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("\n" + "=" * 60 + "\n")
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)
