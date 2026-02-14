import time
import requests
from datetime import datetime
from dotenv import load_dotenv
import os
ENV_FILE = "auth_tokens.env"
load_dotenv(ENV_FILE)
# --- CONFIGURATION ---
REFRESH_URL = "http://damens-server.local:8000/test-refresh"
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# 12 Hours in seconds (12 * 60 * 60)
INTERVAL_SECONDS = 43200 

def send_discord_alert(message):
    """Sends a notification to your Discord channel."""
    try:
        payload = {"content": message}
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=5)
    except Exception as e:
        print(f"⚠️ Failed to send Discord alert: {e}")

def trigger_refresh():
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} 🔄 Sending refresh request...")
    
    try:
        # Timeout set to 10s to prevent hanging
        response = requests.get(REFRESH_URL, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Grab last 10 chars of token for verification
            token_preview = data.get('newToken', 'Unknown')[-10:] if data.get('newToken') else "N/A"
            
            msg = (
                f"✅ **Token Refreshed Successfully**\n"
                f"🕒 Time: `{timestamp}`\n"
                f"🔑 New Token Ends: `...{token_preview}`\n"
                f"🔄 Next Refresh: in 12 hours"
            )
            print(f"{timestamp} Success.")
            send_discord_alert(msg)
            
        else:
            error_msg = (
                f"⚠️ **Refresh Warning**\n"
                f"Server returned code: `{response.status_code}`\n"
                f"Response: `{response.text}`"
            )
            print(f"{timestamp} Warning: {response.status_code}")
            send_discord_alert(error_msg)
            
    except Exception as e:
        fail_msg = (
            f"❌ **CRITICAL FAILURE**\n"
            f"Could not reach server at `{REFRESH_URL}`\n"
            f"Error: `{str(e)}`"
        )
        print(f"{timestamp} Error: {e}")
        send_discord_alert(fail_msg)

if __name__ == "__main__":
    print(f"🚀 Keep-Alive Service Started")
    print(f"🎯 Target: {REFRESH_URL}")
    print(f"⏱️  Interval: Every 12 hours")
    
    # Send a startup notification
    send_discord_alert(f"🚀 **Keep-Alive Script Started**\nMonitoring: `{REFRESH_URL}`\nInterval: 12 Hours")
    
    # Run immediately on startup
    trigger_refresh()

    # Loop forever
    while True:
        time.sleep(INTERVAL_SECONDS)
        trigger_refresh()