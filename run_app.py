#!/usr/bin/env python3
"""
This is a launcher script for the AI Travel Magic application.
Run this script to start the Streamlit server manually.
"""

import os
import subprocess
import webbrowser
import time

def main():
    print("🚀 Starting AI Travel Magic application...")
    
    # Create .streamlit directory if it doesn't exist
    if not os.path.exists('.streamlit'):
        os.makedirs('.streamlit')
    
    # Make sure config.toml exists with proper server settings
    config_path = '.streamlit/config.toml'
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            f.write("""
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6" 
textColor = "#262730"
font = "sans serif"
            """)
    
    # Start the Streamlit server
    print("📋 Starting Streamlit server...")
    
    # Run the Streamlit process
    streamlit_process = subprocess.Popen([
        "streamlit", "run", "main.py",
        "--server.port=5000",
        "--server.address=0.0.0.0",
        "--server.headless=true"
    ])
    
    # Wait a bit for the server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Try to open the browser
    server_url = "http://localhost:5000"
    try:
        print(f"🌐 Opening browser at {server_url}")
        webbrowser.open(server_url)
    except:
        print(f"⚠️ Could not open browser automatically. Please navigate to: {server_url}")
    
    print("✅ Streamlit server is running!")
    print("ℹ️ Press Ctrl+C to stop the server")
    
    # Keep the server running until keyboard interrupt
    try:
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        streamlit_process.terminate()
        print("👋 Server stopped. Thank you for using AI Travel Magic!")

if __name__ == "__main__":
    main()