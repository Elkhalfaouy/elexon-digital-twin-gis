"""
Generate a shareable public link for the Streamlit app
Run this after starting your Streamlit app on localhost:8501
"""
from pyngrok import ngrok
import time

# Open a ngrok tunnel to port 8501 (Streamlit default)
print("Creating public shareable link...")
print("Make sure your Streamlit app is running on http://localhost:8501")
print("-" * 60)

public_url = ngrok.connect(8501)
print(f"\n✅ PUBLIC LINK CREATED!")
print(f"🔗 Share this link with your supervisors:\n")
print(f"   {public_url}")
print(f"\n⚠️ This link will work as long as:")
print(f"   1. Your Streamlit app is running")
print(f"   2. This script is running")
print(f"   3. Your computer is connected to the internet")
print("\nPress Ctrl+C to stop sharing...")
print("-" * 60)

try:
    # Keep the tunnel alive
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nStopping public link...")
    ngrok.kill()
    print("Link closed.")
