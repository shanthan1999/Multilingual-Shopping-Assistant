#!/usr/bin/env python3
"""
Simple script to run the Regional Shopping AI Streamlit application
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit application"""
    try:
        # Change to the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        
        print("🚀 Starting Regional Shopping AI Streamlit App...")
        print("📍 Project directory:", project_dir)
        print("🌐 The app will open in your default browser")
        print("⏹️  Press Ctrl+C to stop the application")
        print("-" * 50)
        
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        print("💡 Make sure you have installed all requirements:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()