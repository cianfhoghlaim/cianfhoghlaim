#!/usr/bin/env python3
"""
Launch script for the Receipt Evaluation Streamlit Dashboard.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the Streamlit app."""
    # Get the path to the streamlit app
    app_path = Path(__file__).parent / "streamlit_app.py"
    
    # Launch streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    
    print("🚀 Launching Receipt Evaluation Dashboard...")
    print(f"Command: {' '.join(cmd)}")
    print("📱 The dashboard will open in your browser automatically.")
    print("🛑 Press Ctrl+C to stop the server.")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")

if __name__ == "__main__":
    main()
