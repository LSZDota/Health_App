# withings_api.py

import requests
import json
import os
from urllib.parse import urlencode

# Replace these with your actual credentials
CLIENT_ID = '4c0441ed25b917cf01d8cccf9efd6b4def85e855e30bc66f91934cdb7bf5f848'
CLIENT_SECRET = 'e02317295a3b34119200877eeab1ac727cd06f8048c7855aab8a77ac07511943'
REDIRECT_URI = 'http://localhost:8501/'  # Streamlit runs on port 8501 by default

# Paths for storing tokens and data
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKENS_FILE_PATH = os.path.join(SCRIPT_DIR, 'saved_data', 'withings_tokens.json')
WEIGHT_DATA_FILE_PATH = os.path.join(SCRIPT_DIR, 'saved_data', 'weight_data.json')

# Ensure the saved_data directory exists
if not os.path.exists(os.path.join(SCRIPT_DIR, 'saved_data')):
    os.makedirs(os.path.join(SCRIPT_DIR, 'saved_data'))

def save_tokens(access_token, refresh_token):
    tokens = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    with open(TOKENS_FILE_PATH, 'w') as f:
        json.dump(tokens, f)

def load_tokens():
    if os.path.exists(TOKENS_FILE_PATH):
        with open(TOKENS_FILE_PATH, 'r') as f:
            tokens = json.load(f)
            return tokens.get('access_token'), tokens.get('refresh_token')
    else:
        return None, None

def get_authorization_url():
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'state': 'withings_auth',
        'redirect_uri': REDIRECT_URI,
        'scope': 'user.metrics'
    }
    url = 'https://account.withings.com/oauth2_user/authorize2?' + urlencode(params)
    return url

def exchange_code_for_tokens(auth_code):
    token_url = 'https://wbsapi.withings.net/v2/oauth2'
    data = {
        'action': 'requesttoken',
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
    }
    response = requests.post(token_url, data=data)
    response_json = response.json()
    if response_json.get('status') == 0:
        tokens = response_json['body']
        save_tokens(tokens['access_token'], tokens['refresh_token'])
        return tokens['access_token'], tokens['refresh_token']
    else:
        return None, None

def refresh_tokens(refresh_token):
    token_url = 'https://wbsapi.withings.net/v2/oauth2'
    data = {
        'action': 'requesttoken',
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token
    }
    response = requests.post(token_url, data=data)
    response_json = response.json()
    if response_json.get('status') == 0:
        tokens = response_json['body']
        save_tokens(tokens['access_token'], tokens['refresh_token'])
        return tokens['access_token']
    else:
        return None

def fetch_measurements(access_token, measure_type):
    url = 'https://wbsapi.withings.net/measure'
    params = {
        'action': 'getmeas',
        'access_token': access_token,
        'meastypes': measure_type,
        'category': 1
    }
    response = requests.get(url, params=params)
    response_json = response.json()
    if response_json.get('status') == 0:
        data = response_json['body']['measuregrps']
        # Save the data to a JSON file
        with open(WEIGHT_DATA_FILE_PATH, 'w') as f:
            json.dump(data, f)
        return data
    else:
        return None
