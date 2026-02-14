import requests
import json

# --- CONFIGURATION ---
# Your Ngrok Webhook URL
WEBHOOK_URL = "http://127.0.0.1:8000/webhook"

def send_test_signal(name, payload):
    print(f"--- Running Test: {name} ---")
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        # Using .get() to avoid crashing if the server doesn't return JSON
        try:
            print(f"Server Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Server Response (Text): {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 30 + "\n")

# --- TEST PAYLOADS ---

# 1. HIGH ORDER SIZE TEST (Verify server-side lot sizing overrides)
test_high_size = {
    "action": "BUY",
    "entry": 19500.50,
    "sl": 19450.00,
    "tp": 19600.00,
    "size": 10, 
    "use_brackets": False, # Forced False
    "time": "2026-02-14 12:00:00"
}

# 2. SELL SIGNAL (Verify short-side logic)
test_sell = {
    "action": "SELL",
    "entry": 19500.00,
    "sl": 19520.00,
    "tp": 19400.00,
    "size": 1,
    "use_brackets": False, # Forced False
    "time": "2026-02-14 12:05:00"
}

# 3. NAKED ORDER (Standard Buy)
test_naked = {
    "action": "BUY",
    "entry": 19000.00,
    "size": 2,
    "use_brackets": False,
    "time": "2026-02-14 12:10:00"
}

# 4. EXIT SIGNAL (Close positions)
test_exit = {
    "action": "EXIT",
    "time": "2026-02-14 12:15:00"
}

# 5. DYNAMIC SIZING TEST (Size = 0)
# Use this to see if your server applies a "Minimum Size" or a default if 0 is passed
test_zero_size = {
    "action": "BUY",
    "entry": 19100.00,
    "size": 0,
    "use_brackets": False,
    "time": "2026-02-14 12:20:00"
}

# 6. MISSING PRICE DATA (Robustness Check)
# Verifies the server doesn't crash if TV fails to send SL/TP prices
test_missing_prices = {
    "action": "BUY",
    "entry": 19200.00,
    "size": 1,
    "use_brackets": False,
    "time": "2026-02-14 12:25:00"
    # Note: 'sl' and 'tp' are missing entirely
}

if __name__ == "__main__":
    print(f"🚀 Starting Automated Webhook Tests against {WEBHOOK_URL}")
    print(f"⚠️  ALL BRACKETS ARE DISABLED IN THESE TESTS\n")
    
    send_test_signal("High Size Overrides", test_high_size)
    send_test_signal("Standard Sell", test_sell)
    send_test_signal("Naked Buy", test_naked)
    send_test_signal("Zero Size Check", test_zero_size)
    send_test_signal("Missing Price Data", test_missing_prices)
    send_test_signal("Exit Signal", test_exit)
    
    print("✅ All test signals dispatched.")