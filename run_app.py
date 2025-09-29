#!/usr/bin/env python3
"""
Music Explorer Launcher Script
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        ('streamlit', 'streamlit'),
        ('pandas', 'pandas'), 
        ('numpy', 'numpy'), 
        ('plotly', 'plotly'),
        ('scikit-learn', 'sklearn'),
        ('umap-learn', 'umap')
    ]
    
    missing_packages = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_data_files():
    """Check if data files exist."""
    data_dir = Path("data")
    required_files = [
        "spotify_tracks_enhanced.csv",
        "spotify_tracks_embedded.csv"
    ]
    
    missing_files = []
    for file in required_files:
        if not (data_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing data files:")
        for file in missing_files:
            print(f"   - data/{file}")
        print("\n💡 Run the data generator:")
        print("   python enhanced_data_generator.py")
        return False
    
    print("✅ Data files are present")
    return True

def run_streamlit_app(app_file):
    """Run the Streamlit application."""
    try:
        print(f"🚀 Starting {app_file}...")
        print("📱 The app will open in your browser automatically")
        print("🛑 Press Ctrl+C to stop the application")
        print("-" * 50)
        
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_file], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running application: {e}")
    except FileNotFoundError:
        print(f"❌ Streamlit not found. Install with: pip install streamlit")

def main():
    """Main launcher function."""
    print("🎵 Music Explorer Map - Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("enhanced_streamlit_app.py").exists():
        print("❌ Please run this script from the music-explorer directory")
        print("   Make sure you're in the folder containing enhanced_streamlit_app.py")
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check data files
    if not check_data_files():
        return
    
    print("\n🎛️ Choose application version:")
    print("1. Enhanced version (recommended) - Modern UI with all features")
    print("2. Basic version - Simple interface")
    print("3. Run tests - Verify everything works")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            run_streamlit_app("enhanced_streamlit_app.py")
            break
        elif choice == "2":
            run_streamlit_app("streamlit_app.py")
            break
        elif choice == "3":
            print("\n🧪 Running test suite...")
            subprocess.run([sys.executable, "test_app.py"], check=True)
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
