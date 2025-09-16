#!/usr/bin/env python3
"""
Test script for text extraction functionality.
This demonstrates how to properly extract text from different file types.
"""

import tempfile
import os
from file_handler import FileHandler

def test_text_extraction():
    """Test text extraction from different file types"""
    print("🧪 Testing Text Extraction Functionality")
    print("=" * 50)
    
    # Initialize file handler
    file_handler = FileHandler()
    
    # Test 1: Create a sample text file
    print("\n1️⃣ Testing Text File Extraction")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
        tmp_file.write("This is a sample job description for a Software Engineer position.")
        tmp_file_path = tmp_file.name
    
    try:
        success, text = file_handler.extract_text(tmp_file_path)
        if success:
            print(f"✅ Text file extraction successful: {text}")
        else:
            print(f"❌ Text file extraction failed: {text}")
    finally:
        os.unlink(tmp_file_path)
    
    # Test 2: Test with existing files if they exist
    print("\n2️⃣ Testing with existing files")
    
    # Check if we have any sample files
    sample_files = [
        'saved_job_descriptions.json',
        'demo_saved_jd.py',
        'app.py'
    ]
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            print(f"\n📁 Testing: {file_path}")
            try:
                success, text = file_handler.extract_text(file_path)
                if success:
                    # Show first 100 characters
                    preview = text[:100] + "..." if len(text) > 100 else text
                    print(f"✅ Success: {preview}")
                else:
                    print(f"❌ Failed: {text}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    print("\n3️⃣ File Handler Methods Available:")
    print("   • extract_text(file_path) - Main extraction method")
    print("   • extract_text_from_pdf(file_path) - PDF specific")
    print("   • extract_text_from_docx(file_path) - DOCX specific")
    print("   • extract_text_from_txt(file_path) - Text specific")
    
    print("\n💡 Key Points:")
    print("   • Always use file_handler.extract_text() instead of reading raw files")
    print("   • This handles PDF, DOCX, and TXT files properly")
    print("   • Avoids the garbled text issue you experienced")
    print("   • Creates temporary files for Streamlit uploaded files")

if __name__ == "__main__":
    test_text_extraction()
