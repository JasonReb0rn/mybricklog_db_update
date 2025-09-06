#!/usr/bin/env python3
"""
Test script to verify the web scraper fixes work correctly.
This script tests just the download and parsing logic without database operations.
"""
import os
import sys
import logging

# Add the current directory to Python path so we can import from update_data
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from update_data import setup_directories, download_and_extract_files

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_scraper():
    """Test the scraper functionality."""
    try:
        print("🔧 Setting up directories...")
        setup_directories()
        
        print("🌐 Testing web scraper...")
        downloaded_files = download_and_extract_files()
        
        print(f"✅ Successfully downloaded {len(downloaded_files)} files:")
        for file in downloaded_files:
            print(f"  - {file}")
        
        # Check if CSV files were created
        csv_files = []
        for gz_file in downloaded_files:
            csv_file = gz_file[:-3]  # Remove .gz extension
            csv_path = os.path.join('temp', csv_file)
            if os.path.exists(csv_path):
                size = os.path.getsize(csv_path)
                csv_files.append(f"{csv_file} ({size:,} bytes)")
        
        print(f"\n📄 CSV files created:")
        for csv_file in csv_files:
            print(f"  - {csv_file}")
        
        return len(downloaded_files) > 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_scraper()
    if success:
        print("\n🎉 Scraper test PASSED!")
        sys.exit(0)
    else:
        print("\n💥 Scraper test FAILED!")
        sys.exit(1)
