import os
import time
import webbrowser

# === SETTINGS ===
PORT = 8501
main_script = "main.py"
config_dir = ".streamlit"
config_path = os.path.join(config_dir, "config.toml")

# === ENVIRONMENT OVERRIDE ===
os.environ["STREAMLIT_SERVER_PORT"] = str(PORT)

# === ENSURE .streamlit/config.toml EXISTS ===
if not os.path.exists(config_dir):
    os.makedirs(config_dir)

with open(config_path, "w") as f:
    f.write(f"""
[server]
port = {PORT}
enableCORS = false
headless = true
""")

# === LOGGING ===
print("🚀 Launching Streamlit App")
print(f"👉 Port: {PORT}")
print(f"👉 Main Script: {main_script}")
print(f"👉 Config path: {os.path.abspath(config_path)}")
print(f"👉 Current working directory: {os.getcwd()}")
print(f"👉 Environment var STREAMLIT_SERVER_PORT: {os.environ['STREAMLIT_SERVER_PORT']}")

# === OPEN THE APP IN BROWSER ===
webbrowser.open(f"http://localhost:{PORT}")

# === RUN STREAMLIT WITH FORCED PORT ===
exit_code = os.system(f"streamlit run {main_script} --server.port {PORT}")

# === POST-RUN WARNING ===
if exit_code != 0:
    print("\n⚠️ Streamlit failed to start. Make sure it's installed and available in PATH.\n")
else:
    print(f"\n✅ Streamlit should be running on http://localhost:{PORT}")
    print("⚠️ If it's not, something external is hijacking the port.")
