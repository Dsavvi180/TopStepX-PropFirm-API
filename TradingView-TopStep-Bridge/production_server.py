import sys
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from pyngrok import ngrok
from dotenv import load_dotenv
import requests
# tmux new -s myserver (run the following commands inside a tmux session - allows server to run in terminal session once detached)
# TO START SERVER: run  sudo python -m gunicorn --preload --workers 2 --threads 4 --worker-class gthread -b 0.0.0.0:8000 production_server:app
# RUN keep_alive.py in the same tmux session different terminal to auto refresh token every 12 hours: python keep_alive.py
# TO DETACH TMUX: Ctrl + B, then D
# TO RE-ATTACH TMUX: tmux attach -t myserver
# TO KILL PROCESSES: sudo pkill -9 -f production_server; sudo pkill -9 -f ngrok
# TO AUTO MANUALLY AUTH TOKEN: http://localhost:8000/test-refresh OR if on Raspberry Pi http://damens-server.local:8000/test-refresh
# Import the local client module
import topstep_client

# Load environment variables from .env file
ENV_FILE = "auth_tokens.env"
load_dotenv(ENV_FILE)
app = Flask(__name__)
PORT = 8000 
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
def send_discord_alert(message):
    """Sends a trade notification to Discord."""
    try:
        payload = {"content": message}
        # Timeout is short (3s) so it doesn't slow down the trading server response
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=3)
    except Exception as e:
        print(f"⚠️ Failed to send Discord alert: {e}")

# --- NGROK SETUP ---
# We check WERKZEUG_RUN_MAIN to ensure ngrok doesn't start twice during Flask reloads
if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
    
    # Retrieve the token safely from the environment
    ngrok_token = os.getenv("NGROK_API_KEY")
    
    if ngrok_token:
        print(f" * Authenticating Ngrok...")
        ngrok.set_auth_token(ngrok_token)

        try:
            public_url = ngrok.connect(PORT).public_url
            print(f" * Ngrok Tunnel URL: {public_url}")
            print(f" * Webhook Endpoint: {public_url}/webhook")
            send_discord_alert(f"🟢 **Server Online**\nTunnel: `{public_url}`")
        except Exception as e:
            print(f" ! Ngrok startup error: {e}")
    else:
        print(" ⚠️  WARNING: NGROK_API_KEY not found in .env file. Tunnel may fail.")

@app.route('/webhook', methods=['POST'])
def webhook_listener():
    print("\n--- [POST] Signal Received ---")
    
    try:
        if request.is_json:
            data = request.json
        else:
            data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

    # 1. Extract Data
    action = data.get("action", "unknown").upper()
    entry = float(data.get("entry", 0))
    sl = float(data.get("sl", 0))
    tp = float(data.get("tp", 0))
    alert_time = data.get("time", "N/A")
    
    # Extract the Bracket Switch (Defaults to False)
    use_brackets = data.get("use_brackets", False) 

    # 2. Log to File
    now = datetime.now()
    
    with open("webhook_logs.txt", "a") as f:
        log_entry = f"Alert: {alert_time} | {action} | Entry: {entry} | Brackets: {use_brackets}\n"
        f.write(log_entry)

    # 3. Execute Trade
    if action in ["BUY", "SELL"]:
        print(f" Triggering Topstep Order: {action} (Brackets: {use_brackets})")
        
        try:
            result = topstep_client.execute_order(
                action=action, 
                entry_price=entry,
                sl_price=sl,
                tp_price=tp,
                use_brackets=use_brackets
            )

            discord_msg = (
                f"🚀 **Order Filled: {action}**\n"
                f"💲 Entry: `{entry}`\n"
                f" SL: `{sl}`\n"
                f" TP: `{tp}`\n"
                f"🛡️ Brackets: `{use_brackets}`\n"
                f"📜 Details: `{str(result)}`"
            )
            send_discord_alert(discord_msg)
            return jsonify({"status": "filled", "details": result}), 200

        except Exception as e:
            print(f" Order Failed: {e}")
            # --- FAILURE ALERT ---
            discord_msg = (
                f"❌ **Order FAILED: {action}**\n"
                f"⚠️ Error: `{str(e)}`"
            )
            send_discord_alert(discord_msg)
            with open("error_log.txt", "a") as f:
                f.write(f"[{datetime.now()}] FAILED: {action} - {e}\n")
            return jsonify({"status": "failed", "error": str(e)}), 500

    elif action == "EXIT":
        print(f" Processing Exit (Log Only)")
        return jsonify({"status": "filled", "details": "Exited trade"}), 200
    else:
        return jsonify({"status": "ignored"}), 200

# --- NEW TEST ENDPOINT ---
@app.route('/test-refresh', methods=['GET'])
def test_refresh():
    """Manually triggers the token refresh logic for testing purposes."""
    print("\n🧪 Manual Test: Triggering Token Refresh...")
    try:
        success = topstep_client.refresh_auth()
        if success:
            load_dotenv("auth_tokens.env", override=True)
            new_token = os.getenv('RENEWED_AUTH')
            return jsonify({"status": "success", "message": "Token refreshed successfully", "new Token": new_token}), 200
        else:
            return jsonify({"status": "failed", "message": "Login call returned False"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(port=PORT)