import os
import json
import time
import requests
import threading
from dotenv import load_dotenv, set_key

# --- CONFIGURATION ---
# Load variables from auth_tokens.env
ENV_FILE = "auth_tokens.env"
load_dotenv(ENV_FILE)

# Static Credentials
TOPSTEP_USER = "quantsavvi"  
ACCOUNT_ID = 16123563
CONTRACT_ID = "CON.F.US.MNQ.H26"
DEFAULT_SIZE = 2

# Endpoints
URL_LOGIN = "https://api.topstepx.com/api/Auth/loginKey"
URL_VALIDATE = "https://api.topstepx.com/api/Auth/validate"
URL_ORDER = "https://api.topstepx.com/api/Order/place"

class AuthManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.token = os.getenv("RENEWED_AUTH")
        self.api_key = os.getenv("INITIAL_AUTH")
        
        # If we have a stored token, validate it. If not, login.
        if not self.validate_current_token():
            print("⚠️ Stored token invalid or missing. Attempting fresh login...")
            self.login()

    def save_token(self, new_token):
        """Writes the new token back to the .env file for persistence"""
        with self.lock:
            self.token = new_token
            # Update the file so it survives restarts
            set_key(ENV_FILE, "RENEWED_AUTH", new_token)

    def validate_current_token(self):
        """Checks if the current REFRESHED_AUTH token is still alive"""
        if not self.token:
            return False
            
        headers = {'Authorization': f"Bearer {self.token}", 'accept': 'text/plain'}
        try:
            r = requests.post(URL_VALIDATE, headers=headers, timeout=5)
            if r.status_code == 200:
                print("✅ [Auth] Stored token is valid.")
                return True
        except:
            pass
        return False

    def login(self):
        """Uses the API Key (INITIAL_AUTH) to get a fresh Session Token"""
        payload = {"userName": TOPSTEP_USER, "apiKey": self.api_key}
        headers = {'Content-Type': 'application/json', 'accept': 'text/plain'}
        
        try:
            r = requests.post(URL_LOGIN, json=payload, headers=headers)
            if r.status_code == 200 and r.json().get('success'):
                new_token = r.json().get('token')
                print(f"✅ [Auth] Fresh Login Successful.")
                self.save_token(new_token)
                return True
            else:
                print(f"❌ [Auth] Login Failed: {r.text}")
        except Exception as e:
            print(f"❌ [Auth] Connection Error: {e}")
        return False

    def get_headers(self):
        """Ensures we have a valid token before returning headers"""
        if not self.token:
            self.login()
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

# Initialize the Auth System
auth = AuthManager()

def execute_order(action, entry_price, sl_price, tp_price):
    """
    Calculates ticks and sends the order to Topstep.
    Returns the API response dict or raises an Exception.
    """
    action = action.lower()
    
    # 1. Tick Math (MNQ = 0.25)
    tick_size = 0.25
    try:
        sl_ticks = int(abs(entry_price - sl_price) / tick_size)
        tp_ticks = int(abs(entry_price - tp_price) / tick_size)
    except ZeroDivisionError:
        raise ValueError("Tick size cannot be zero.")

    # 2. Logic: Buy vs Sell (Side & Bracket Signs)
    if action == 'buy':
        side_code = 0 
        final_sl = -sl_ticks  # Buy: Stop is below (negative ticks)
        final_tp = tp_ticks   # Buy: Target is above (positive ticks)
    elif action == 'sell':
        side_code = 1
        final_sl = sl_ticks   # Sell: Stop is above (positive ticks)
        final_tp = -tp_ticks  # Sell: Target is below (negative ticks)
    else:
        raise ValueError(f"Unknown action: {action}")

    # 3. Payload Construction
    payload = {
        "accountId": ACCOUNT_ID,
        "contractId": CONTRACT_ID,
        "type": 2, # Market Order
        "side": side_code,
        "size": DEFAULT_SIZE,
        "stopLossBracket": {
            "type": 4, # Ticks
            "ticks": final_sl
        },
        "takeProfitBracket": {
            "type": 1, # Ticks
            "ticks": final_tp
        }
    }

    print(f"⚙️  Sending Order: {action.upper()} {DEFAULT_SIZE}x {CONTRACT_ID}")
    
    # 4. Send Request
    response = requests.post(URL_ORDER, json=payload, headers=auth.get_headers(), timeout=5)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")