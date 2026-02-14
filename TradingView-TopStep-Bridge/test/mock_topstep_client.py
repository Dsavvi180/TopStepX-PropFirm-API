# mock_client.py
import time
import random

def refresh_auth():
    """Mocks the authentication refresh."""
    print("\n[MOCK] 🔄 Pretending to refresh token...")
    time.sleep(1) # Simulate network delay
    print("[MOCK] ✅ Token 'refreshed' successfully.")
    return True

def execute_order(accountID, action, entry_price=0, sl_price=0, tp_price=0, use_brackets=False, quantity=1):
    """
    Mocks placing an order.
    Returns a fake success response so the server thinks it worked.
    """
    print(f"\n[MOCK] 🛒 ORDER RECEIVED for Account: {accountID}")
    print(f"       Action: {action} | Size: {quantity}")
    
    if use_brackets:
        print(f"       Brackets: ON | Entry: {entry_price} | SL: {sl_price} | TP: {tp_price}")
    else:
        print(f"       Brackets: OFF (Naked Order)")

    # Simulate network delay
    time.sleep(0.5)

    # Return a fake API response exactly like Topstep would send
    return {
        "status": "filled",
        "orderId": f"mock_order_{random.randint(1000, 9999)}",
        "account": accountID,
        "filledQuantity": quantity,
        "timestamp": time.ctime()
    }