#!/usr/bin/env python3
"""
Installation script for the Resume-Job Description Comparison Application.
This script helps set up the environment and download required models.
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ is required. Current version: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    
    # Upgrade pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def download_spacy_model():
    """Download the required spaCy model."""
    print("📚 Downloading spaCy model...")
    
    if not run_command("python -m spacy download en_core_web_sm", "Downloading spaCy model"):
        return False
    
    return True

def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing imports...")
    
    required_modules = [
        'sklearn',
        'spacy',
        'transformers',
        'torch',
        'streamlit',
        'pdfplumber',
        'docx',
        'numpy',
        'pandas',
        'plotly'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All modules imported successfully")
    return True

def test_spacy_model():
    """Test if the spaCy model is working."""
    print("🧪 Testing spaCy model...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        
        # Test with a simple sentence
        doc = nlp("This is a test sentence.")
        print(f"✅ spaCy model working. Processed sentence with {len(doc)} tokens")
        return True
        
    except Exception as e:
        print(f"❌ spaCy model test failed: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    
    directories = ['temp', 'uploads', 'outputs']
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

def run_demo():
    """Run a quick demo to test the installation."""
    print("🚀 Running demo...")
    
    if not run_command("python demo.py", "Running demo"):
        print("⚠️ Demo failed, but installation might still be successful")
        return True
    
    return True

def main():
    """Main installation function."""
    print("🏭 I Knowledge Factory Pvt. Ltd.")
    print("🚀 Resume-Job Description Comparison Application")
    print("=" * 50)
    print("Installation script")
    print("=" * 50)
    
    # Check system info
    print(f"🖥️  Operating System: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Installation failed. Please check the error messages above.")
        sys.exit(1)
    
    # Download spaCy model
    if not download_spacy_model():
        print("\n❌ Failed to download spaCy model.")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n❌ Some modules failed to import.")
        sys.exit(1)
    
    # Test spaCy model
    if not test_spacy_model():
        print("\n❌ spaCy model test failed.")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\n❌ Failed to create directories.")
        sys.exit(1)
    
    # Run demo
    print("\n🎯 Installation completed successfully!")
    print("Running demo to verify everything works...")
    
    if run_demo():
        print("\n🎉 Installation and demo completed successfully!")
        print("\n📚 To run the application:")
        print("   streamlit run app.py")
        print("\n📖 To run the demo again:")
        print("   python demo.py")
        print("\n📁 Application files:")
        print("   - app.py: Main Streamlit application")
        print("   - demo.py: Demo script")
        print("   - README.md: Documentation")
    else:
        print("\n⚠️ Installation completed but demo failed.")
        print("The application might still work. Try running:")
        print("   streamlit run app.py")

if __name__ == "__main__":
    main()
