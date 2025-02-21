import requests
import json
import os
import time
from datetime import datetime

# Replace these with your actual tokens and user ID
USER_ID = '38378503'
CLIENT_ID = '4c0441ed25b917cf01d8cccf9efd6b4def85e855e30bc66f91934cdb7bf5f848'
CLIENT_SECRET = 'e02317295a3b34119200877eeab1ac727cd06f8048c7855aab8a77ac07511943'
REDIRECT_URI = 'http://localhost:5000/callback'
TOKENS_FILE = 'withings_tokens.json'


# Ensure the tokens file is in the saved_data directory
if not os.path.exists('saved_data'):
    os.makedirs('saved_data')

TOKENS_FILE_PATH = os.path.join('saved_data', TOKENS_FILE)
WEIGHT_DATA_FILE_PATH = os.path.join('saved_data', 'weight_data.json')


# ----------------------------- Token Functions -----------------------------

def load_tokens():
    if os.path.exists(TOKENS_FILE_PATH):
        with open(TOKENS_FILE_PATH, 'r') as f:
            tokens = json.load(f)
            return tokens.get('access_token'), tokens.get('refresh_token')
    else:
        return None, None

def save_tokens(access_token, refresh_token):
    tokens = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    with open(TOKENS_FILE_PATH, 'w') as f:
        json.dump(tokens, f)
    print(f"Tokens saved to {TOKENS_FILE_PATH}")

def refresh_tokens(refresh_token):
    token_url = 'https://wbsapi.withings.net/v2/oauth2'
    token_data = {
        'action': 'requesttoken',
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token
    }

    response = requests.post(token_url, data=token_data)
    response_json = response.json()

    if response_json.get('status') == 0:
        tokens = response_json['body']
        access_token = tokens['access_token']
        new_refresh_token = tokens['refresh_token']
        save_tokens(access_token, new_refresh_token)
        print("Tokens refreshed successfully.")
        return access_token, new_refresh_token
    else:
        print("Error refreshing tokens:", response_json)
        return None, None
    


def fetch_measurements(access_token):
    url = 'https://wbsapi.withings.net/measure'
    params = {
        'action': 'getmeas',
        'access_token': access_token,
        'meastypes': 1,  # Weight measurements
        'category': 1    # Real measurements
    }
    response = requests.get(url, params=params)
    response_json = response.json()

    if response_json.get('status') == 0:
        data = response_json['body']['measuregrps']
        # Save the data to a JSON file
        with open(WEIGHT_DATA_FILE_PATH, 'w') as f:
            json.dump(data, f)
        print(f"Data saved to {WEIGHT_DATA_FILE_PATH}")
        return True
    else:
        print("Error fetching measurements:", response_json)
        return False

# ----------------------------- Main Execution -----------------------------

if __name__ == '__main__':
    access_token, refresh_token = load_tokens()

    if not access_token or not refresh_token:
        print("Tokens not found. Please run 'withings_auth.py' to authenticate.")
    else:
        # Try fetching measurements
        success = fetch_measurements(access_token)
        if not success:
            print("Access token may have expired. Attempting to refresh tokens...")
            access_token, refresh_token = refresh_tokens(refresh_token)
            if access_token:
                # Retry fetching measurements with the new access token
                fetch_measurements(access_token)
            else:
                print("Failed to refresh tokens. Please re-authenticate using 'withings_auth.py'.")

