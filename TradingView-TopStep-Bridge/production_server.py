import sys
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from pyngrok import ngrok
from dotenv import load_dotenv  # Import dotenv

# Import the local client module
import topstep_client

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
PORT = 8000 

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
    formatted_time = now.strftime("[%Y-%m-%d %H:%M:%S]")
    
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
            return jsonify({"status": "filled", "details": result}), 200

        except Exception as e:
            print(f" Order Failed: {e}")
            with open("error_log.txt", "a") as f:
                f.write(f"[{datetime.now()}] FAILED: {action} - {e}\n")
            return jsonify({"status": "failed", "error": str(e)}), 500

    elif action == "EXIT":
        print(f" Processing Exit (Log Only)")
        return jsonify({"status": "filled", "details": "Exited trade"}), 200
    else:
        return jsonify({"status": "ignored"}), 200

if __name__ == '__main__':
    app.run(port=PORT)
