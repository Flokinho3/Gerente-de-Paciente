import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def poll_only():
    print("Polling events...")
    try:
        resp = requests.get(f"{BASE_URL}/api/events/poll")
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(json.dumps(data, indent=2))
        else:
            print("Server returned error")
            
    except Exception as e:
        print(f"Poll failed: {e}")

if __name__ == "__main__":
    poll_only()
