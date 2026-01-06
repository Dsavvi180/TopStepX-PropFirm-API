import sys
import os
from flask import Flask, request, jsonify
from pyngrok import ngrok
from datetime import datetime

# TO START SERVER: run  sudo python -m gunicorn --preload --workers 2 --threads 4 --worker-class gthread -b 0.0.0.0:8000 production_server:app
import topstep_client

app = Flask(__name__)

# --- CONFIGURATION ---
PORT = 8000 

# --- NGROK SETUP (Standard) ---
if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
    # Ensure this token matches your paid/free account
    # Replace "YOUR_REAL_AUTH_TOKEN_HERE" with your actual token
    ngrok.set_auth_token("30WF6yVOhqSG4f2wRBjzZU6qWzm_5mfgb1k8BFnrPNN6AcRVz") 

    try:
        public_url = ngrok.connect(PORT).public_url
        print(f" * Ngrok Tunnel URL: {public_url}")
        print(f" * Webhook Endpoint: {public_url}/webhook")
    except Exception as e:
        print(f" ! Ngrok startup error: {e}")

@app.route('/webhook', methods=['POST'])
def webhook_listener():
    print("\n--- [POST] Signal Received ---")
    
    # 1. Parse JSON safely
    try:
        if request.is_json:
            data = request.json
        else:
            import json
            data = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        print(f"[ERROR] JSON Parse: {e}")
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

    # 2. Extract Data (Including the new Time field)
    # Format: {"action": "buy", "entry": 100, "sl": 90, "tp": 120, "time": "[2025-12-28 13:54:52]"}
    action = data.get("action", "unknown").upper()
    entry = float(data.get("entry", 0))
    sl = float(data.get("sl", 0))
    tp = float(data.get("tp", 0))
    
    # Get the time string provided by TradingView (default to 'N/A' if missing)
    alert_time = data.get("time", "N/A") 
    # 1. Get the current time
    now = datetime.now()

# 2. Format the time
# We add the brackets [] manually inside the format string
    formatted_time = now.strftime("[%Y-%m-%d %H:%M:%S]")
    # 3. Log to File (With Alert Time)
    with open("webhook_logs.txt", "a") as f:
        # We log the specific Alert Time from the JSON, and the Action details
        log_entry = f"Alert Time: {alert_time}, Logged Time: {formatted_time} | Action: {action} | Entry: {entry} | SL: {sl} | TP: {tp}\n"
        f.write(log_entry)

    # 4. Execute Trade
    if action in ["BUY", "SELL"]:
        print(f" Triggering Topstep Order: {action} (Alert Time: {alert_time})")
        
        try:
            # Pass data to the client module
            result = topstep_client.execute_order(
                action=action, 
                entry_price=entry, 
                sl_price=sl, 
                tp_price=tp
            )
            
            print(f" Topstep Success: {result}")
            return jsonify({"status": "filled", "details": result}), 200

        except Exception as e:
            print(f" Order Failed: {e}")
            # Optional: Log errors to a separate error file
            with open("error_log.txt", "a") as f:
                f.write(f"[{datetime.now()}] FAILED: {action} - {e}\n")
            
            return jsonify({"status": "failed", "error": str(e)}), 500
    elif action == "EXIT":
        print(f" Processing Exit Signal (Alert Time: {alert_time})")
        return jsonify({"status": "filled", "details": "Exited trade"}), 200
    else:
        print(f" Ignoring Action: {action}")
        return jsonify({"status": "ignored"}), 200

if __name__ == '__main__':
    # Fallback for dev testing
    app.run(port=PORT)