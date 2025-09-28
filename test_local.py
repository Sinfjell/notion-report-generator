#!/usr/bin/env python3
"""
Local testing script for the Notion Report Generator.

This script helps you test the application locally before deploying to Google Cloud.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.main import generate_report
from app.settings import settings


async def test_notion_connection():
    """Test basic Notion API connectivity."""
    print("🔍 Testing Notion API connection...")
    
    if not settings.notion_api_token:
        print("❌ ERROR: Notion API token not set!")
        print("   Please set NOTION_API_TOKEN environment variable or create a .env file")
        return False
    
    try:
        from app.notion import notion_api
        # Try to fetch a simple page (this will fail if token is invalid)
        # We'll use a dummy page ID that should return a 400/404, but that's better than auth error
        await notion_api.get_page("dummy-page-id")
    except Exception as e:
        if "401" in str(e) or "Unauthorized" in str(e):
            print("❌ ERROR: Invalid Notion API token!")
            return False
        elif "404" in str(e) or "400" in str(e):
            print("✅ Notion API token is valid (got expected error for dummy page)")
            return True
        else:
            print(f"⚠️  Unexpected error: {e}")
            return False
    
    return True


async def test_storage():
    """Test local storage functionality."""
    print("🔍 Testing local storage...")
    
    try:
        from app.storage import upload_text_public_flexible
        
        test_content = "This is a test report generated locally."
        test_path = "test/test-report.txt"
        
        result_url = upload_text_public_flexible(test_path, test_content)
        
        if result_url.startswith("file://"):
            file_path = result_url.replace("file://", "")
            if os.path.exists(file_path):
                print(f"✅ Local storage working! Test file saved to: {file_path}")
                return True
            else:
                print(f"❌ ERROR: File not found at {file_path}")
                return False
        else:
            print(f"✅ Storage working! URL: {result_url}")
            return True
            
    except Exception as e:
        print(f"❌ ERROR: Storage test failed: {e}")
        return False


async def test_full_workflow(page_id: str):
    """Test the full report generation workflow."""
    print(f"🔍 Testing full workflow with page ID: {page_id}")
    
    try:
        result = await generate_report(page_id)
        print("✅ Report generation successful!")
        print(f"   Project: {result.get('project_title', 'Unknown')}")
        print(f"   Notes: {result.get('notes_count', 0)}")
        print(f"   Tasks: {result.get('tasks_count', 0)}")
        print(f"   URL: {result.get('url', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ ERROR: Report generation failed: {e}")
        return False


def print_setup_instructions():
    """Print setup instructions for the user."""
    print("\n" + "="*60)
    print("🚀 NOTION REPORT GENERATOR - LOCAL TESTING SETUP")
    print("="*60)
    print()
    print("1. Get your Notion API token:")
    print("   - Go to https://www.notion.so/my-integrations")
    print("   - Create a new integration")
    print("   - Copy the 'Internal Integration Token'")
    print()
    print("2. Set up environment variables:")
    print("   Option A - Environment variable:")
    print("   export NOTION_API_TOKEN='your_token_here'")
    print()
    print("   Option B - Create .env file:")
    print("   echo 'NOTION_API_TOKEN=your_token_here' > .env")
    print()
    print("3. Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    print("4. Run this test script:")
    print("   python test_local.py")
    print()
    print("5. Test with a real page ID:")
    print("   python test_local.py --page-id YOUR_PAGE_ID")
    print()
    print("="*60)


async def main():
    """Main test function."""
    print("🧪 Notion Report Generator - Local Testing")
    print("=" * 50)
    
    # Check if page ID provided as argument
    page_id = None
    if len(sys.argv) > 1 and sys.argv[1] == "--page-id" and len(sys.argv) > 2:
        page_id = sys.argv[2]
    
    # Test 1: Notion API connection
    notion_ok = await test_notion_connection()
    if not notion_ok:
        print_setup_instructions()
        return
    
    # Test 2: Local storage
    storage_ok = await test_storage()
    if not storage_ok:
        print("❌ Storage test failed. Check file permissions.")
        return
    
    print("\n✅ Basic tests passed! The app is ready for local testing.")
    
    # Test 3: Full workflow (if page ID provided)
    if page_id:
        print(f"\n🔍 Testing with real page ID: {page_id}")
        workflow_ok = await test_full_workflow(page_id)
        if workflow_ok:
            print("\n🎉 Full workflow test successful!")
        else:
            print("\n❌ Full workflow test failed. Check the page ID and permissions.")
    else:
        print("\n💡 To test with a real Notion page, run:")
        print("   python test_local.py --page-id YOUR_PAGE_ID")
        print("\n   (Get the page ID from the Notion page URL)")


if __name__ == "__main__":
    asyncio.run(main())
