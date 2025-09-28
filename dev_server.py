#!/usr/bin/env python3
"""
Development server for local testing.

This script starts the FastAPI server with local storage enabled.
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Set local storage as default
os.environ.setdefault("USE_LOCAL_STORAGE", "true")
os.environ.setdefault("LOCAL_STORAGE_PATH", "./local_reports")

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    print("🚀 Starting Notion Report Generator (Local Development Mode)")
    print("=" * 60)
    print("📁 Reports will be saved to: ./local_reports/")
    print("🌐 Server will be available at: http://localhost:8080")
    print("📖 API docs available at: http://localhost:8080/docs")
    print("=" * 60)
    print()
    
    # Check if Notion API token is set
    if not os.getenv("NOTION_API_TOKEN"):
        print("⚠️  WARNING: NOTION_API_TOKEN not set!")
        print("   Set it with: export NOTION_API_TOKEN='your_token_here'")
        print("   Or create a .env file with: NOTION_API_TOKEN=your_token_here")
        print()
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8080,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
