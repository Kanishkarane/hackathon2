#!/usr/bin/env python3
"""
This is a launcher script specifically designed for running 
the AI Travel Magic application in a local environment.
"""

import os
import subprocess
import sys
import webbrowser
import time
import platform

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import streamlit
        import pandas
        import requests
        print("✅ All required dependencies are installed.")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing required dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "pandas", "requests"])
            print("✅ Dependencies installed successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to install dependencies: {e}")
            print("Please install the following manually:")
            print("  - streamlit")
            print("  - pandas")
            print("  - requests")
            return False

def create_config():
    """Create Streamlit configuration file"""
    # Create .streamlit directory if it doesn't exist
    if not os.path.exists('.streamlit'):
        os.makedirs('.streamlit')
    
    # Create config.toml with correct settings
    config_path = '.streamlit/config.toml'
    with open(config_path, 'w') as f:
        f.write("""
[server]
headless = false
address = "localhost"
port = 8501

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
        """)
    print(f"✅ Created Streamlit config at {config_path}")

def main():
    """Main function to run the app locally"""
    print("🚀 Starting AI Travel Magic application locally...")
    
    # Check if required packages are installed
    if not check_dependencies():
        return
    
    # Create proper Streamlit configuration for local use
    create_config()
    
    # Detect the operating system
    system = platform.system().lower()
    
    # Get a free port (default to 8501 which is Streamlit's default)
    port = 8501
    
    # Start the Streamlit server with appropriate settings for local environment
    print(f"📋 Starting Streamlit server on port {port}...")
    
    # Command to run Streamlit (with different syntax based on OS)
    if system == 'windows':
        command = [sys.executable, "-m", "streamlit", "run", "main.py", "--server.port", str(port)]
    else:
        command = ["streamlit", "run", "main.py", "--server.port", str(port)]
    
    # Run the Streamlit process
    streamlit_process = subprocess.Popen(command)
    
    # Wait for the server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    # Open the app in the browser
    server_url = f"http://localhost:{port}"
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