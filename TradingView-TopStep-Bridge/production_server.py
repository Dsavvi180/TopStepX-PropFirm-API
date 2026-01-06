import os
import requests
import threading
from dotenv import load_dotenv, set_key

# --- CONFIGURATION ---
ENV_FILE = "auth_tokens.env"
load_dotenv(ENV_FILE)

# Static Credentials
TOPSTEP_USER = "quantsavvi"   
ACCOUNT_ID = 16123578  
CONTRACT_ID = "CON.F.US.MNQ.H26"
DEFAULT_SIZE = 2
TICK_SIZE = 0.25 # MNQ Tick Size

# Endpoints
URL_LOGIN = "https://api.topstepx.com/api/Auth/loginKey"
URL_VALIDATE = "https://api.topstepx.com/api/Auth/validate"
URL_ORDER = "https://api.topstepx.com/api/Order/place"

class AuthManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.token = os.getenv("RENEWED_AUTH")
        self.api_key = os.getenv("INITIAL_AUTH")
        
        if not self.validate_current_token():
            print("⚠️ Stored token invalid or missing. Attempting fresh login...")
            self.login()

    def save_token(self, new_token):
        with self.lock:
            self.token = new_token
            set_key(ENV_FILE, "RENEWED_AUTH", new_token)

    def validate_current_token(self):
        if not self.token:
            return False
        headers = {'Authorization': f"Bearer {self.token}", 'accept': 'text/plain'}
        try:
            r = requests.post(URL_VALIDATE, headers=headers, timeout=5)
            if r.status_code == 200:
                return True
        except:
            pass
        return False

    def login(self):
        payload = {"userName": TOPSTEP_USER, "apiKey": self.api_key}
        headers = {'Content-Type': 'application/json', 'accept': 'text/plain'}
        try:
            r = requests.post(URL_LOGIN, json=payload, headers=headers)
            if r.status_code == 200 and r.json().get('success'):
                new_token = r.json().get('token')
                self.save_token(new_token)
                return True
            else:
                print(f"❌ [Auth] Login Failed: {r.text}")
        except Exception as e:
            print(f"❌ [Auth] Connection Error: {e}")
        return False

    def get_headers(self):
        if not self.token:
            self.login()
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

auth = AuthManager()

def execute_order(action, entry_price=0, sl_price=0, tp_price=0, use_brackets=False):
    """
    Sends order to Topstep. 
    If use_brackets=True, calculates ticks and attaches SL/TP.
    """
    action = action.lower()

    # 1. Base Payload (Always required)
    side_code = 0 if action == 'buy' else 1
    
    payload = {
        "accountId": ACCOUNT_ID,
        "contractId": CONTRACT_ID,
        "type": 2, # Market Order
        "side": side_code,
        "size": DEFAULT_SIZE
    }

    # 2. Conditional Bracket Logic
    if use_brackets:
        if entry_price == 0 or sl_price == 0 or tp_price == 0:
            raise ValueError("Brackets requested but Price/SL/TP is missing or zero.")

        # Calculate Ticks
        try:
            sl_ticks = int(abs(entry_price - sl_price) / TICK_SIZE)
            tp_ticks = int(abs(entry_price - tp_price) / TICK_SIZE)
        except ZeroDivisionError:
            raise ValueError("Tick size cannot be zero.")

        # Determine Signs based on Side
        if action == 'buy':
            final_sl = -sl_ticks  # Buy: Stop below (negative)
            final_tp = tp_ticks   # Buy: Target above (positive)
        else: # sell
            final_sl = sl_ticks   # Sell: Stop above (positive)
            final_tp = -tp_ticks  # Sell: Target below (negative)

        # Append Brackets to Payload
        # NOTE: Using types 4 and 1 per your original snippet
        payload["stopLossBracket"] = { "type": 4, "ticks": final_sl }
        payload["takeProfitBracket"] = { "type": 1, "ticks": final_tp }
        
        mode_msg = f"w/ Brackets (SL: {sl_price}, TP: {tp_price})"
    else:
        mode_msg = "NAKED (No SL/TP)"

    print(f"⚙️  Sending Order: {action.upper()} {DEFAULT_SIZE}x | {mode_msg}")
    
    # 3. Send Request
    response = requests.post(URL_ORDER, json=payload, headers=auth.get_headers(), timeout=5)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")
