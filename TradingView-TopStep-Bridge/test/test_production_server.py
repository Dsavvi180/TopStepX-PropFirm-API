import sys
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from pyngrok import ngrok
from dotenv import load_dotenv
import requests
import mock_topstep_client as topstep_client_mock

####
# to run: python production_server.py
###
# tmux new -s myserver (run the following commands inside a tmux session - allows server to run in terminal session once detached)
# TO START SERVER: run  sudo python -m gunicorn --preload --workers 2 --threads 4 --worker-class gthread -b 0.0.0.0:8000 production_server:app
# RUN keep_alive.py in the same tmux session different terminal to auto refresh token every 12 hours: python keep_alive.py
# TO DETACH TMUX: Ctrl + B, then D
# TO RE-ATTACH TMUX: tmux attach -t myserver
# TO KILL PROCESSES: sudo pkill -9 -f production_server; sudo pkill -9 -f ngrok
# TO AUTO MANUALLY AUTH TOKEN: http://localhost:8000/test-refresh OR if on Raspberry Pi http://damens-server.local:8000/test-refresh


# --- CONFIGURATION ---
# Load environment variables from .env file
ENV_FILE = "auth_tokens.env"
load_dotenv(ENV_FILE)

app = Flask(__name__)
PORT = 8000 
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# Override JSON order size:
ACCOUNT_1 = os.getenv("ACCOUNT_ID_1")
ACCOUNT_2 = os.getenv("ACCOUNT_ID_2")
ACCOUNT_3 = os.getenv("ACCOUNT_ID_3")
ACCOUNT_4 = os.getenv("ACCOUNT_ID_4")
ACCOUNT_5 = os.getenv("ACCOUNT_ID_5")

# Set contract sizes for each account individually (if override is enabled)
OVERRIDE_SIZE_TRUE = True
OVERRIDE_SIZE = {ACCOUNT_1: 1, ACCOUNT_3: 1, ACCOUNT_2: 3, ACCOUNT_4: 3, ACCOUNT_5: 3}

# Load Account IDs from environment variables
# This creates a list of IDs and filters out any empty ones (None or "")
ACCOUNTS = [
    ACCOUNT_1,
    ACCOUNT_2,
    ACCOUNT_3,
    ACCOUNT_4,
    ACCOUNT_5
]
ACCOUNTS = [acc for acc in ACCOUNTS if acc] # Filter out empty slots

def send_discord_alert(message):
    """Sends a trade notification to Discord."""
    if not DISCORD_WEBHOOK:
        return
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
    
    # Extract Order Size (Check for 'size' or 'quantity', defaults to 2)
    order_size = int(data.get("size", data.get("quantity", 2)))
    
    # Extract the Bracket Switch (Defaults to False)
    use_brackets = data.get("use_brackets", False) 

    # 2. Log to File
    with open("webhook_logs.txt", "a") as f:
        log_entry = f"Alert: {alert_time} | {action} | Size: {order_size} | Entry: {entry} | Brackets: {use_brackets}\n"
        f.write(log_entry)

    # 3. Execute Trade Loop
    results = [] # To store status of each account
    
    if action in ["BUY", "SELL"]:
        print(f" Triggering Topstep Orders: {action} {order_size}x (Brackets: {use_brackets})")
        
        # Loop through ALL accounts in the list
        for accountID in ACCOUNTS:
            print(f" >> Processing Account {accountID}...")
            current_size = order_size
            if OVERRIDE_SIZE_TRUE and accountID in OVERRIDE_SIZE:
                current_size = OVERRIDE_SIZE.get(accountID, current_size) # Use override size if specified for this account

            try:
                # Execute order for this specific account
                # Ensure 'accountID' here matches the argument name in topstep_client.execute_order
                result = topstep_client_mock.execute_order(
                    accountID=accountID,
                    action=action, 
                    entry_price=entry,
                    sl_price=sl,
                    tp_price=tp,
                    use_brackets=use_brackets,
                    quantity=current_size
                )

                # Send success alert for this account
                discord_msg = (
                    f"🚀 **Order sent to TopStep**\n"
                    f"🆔 Account: `{accountID}`\n"
                    f"Action: `{action}` | Size: `{current_size}`\n"
                    f"📜 Details: `{str(result)}`"
                )
                print(action)
                send_discord_alert(discord_msg)
                
                # Add success to results list
                results.append({"account": accountID, "status": "filled", "details": result})

            except Exception as e:
                print(f" ❌ Order Failed for {accountID}: {e}")
                
                # Send failure alert for this account
                discord_msg = (
                    f"❌ **Order FAILED**\n"
                    f"🆔 Account: `{accountID}`\n"
                    f"⚠️ Error: `{str(e)}`"
                )
                send_discord_alert(discord_msg)
                
                # Log error to file
                with open("error_log.txt", "a") as f:
                    f.write(f"[{datetime.now()}] FAILED ACC {accountID}: {e}\n")
                
                # Add failure to results list
                results.append({"account": accountID, "status": "failed", "error": str(e)})
                
                # Continue to the next account!
                continue

        # 4. Return Final Summary (After loop finishes)
        return jsonify({"status": "processed", "results": results}), 200

    elif action == "EXIT":
        print(f" Processing Exit (Log Only)")
        return jsonify({"status": "filled", "details": "Exited trade"}), 200
    else:
        return jsonify({"status": "ignored"}), 200

# --- TEST ENDPOINT ---
@app.route('/test-refresh', methods=['GET'])
def test_refresh():
    """Manually triggers the token refresh logic for testing purposes."""
    print("\n🧪 Manual Test: Triggering Token Refresh...")
    try:
        success = topstep_client_mock.refresh_auth()
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