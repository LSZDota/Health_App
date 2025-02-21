import requests
import json

import os
from withings_api import WithingsApi, AuthScope
from withings_api.common import MeasureType
from withings_api.common import get_measure_value
from datetime import datetime

# Replace these with your actual tokens and user ID
ACCESS_TOKEN = '627d288edc524f03ae3c78d64e7e717d97fa867c'
REFRESH_TOKEN = '74921286ad796bea2882f4e29237287e1b8fb65f'
USER_ID = '38378503'
CLIENT_ID = '4c0441ed25b917cf01d8cccf9efd6b4def85e855e30bc66f91934cdb7bf5f848'
CLIENT_SECRET = 'e02317295a3b34119200877eeab1ac727cd06f8048c7855aab8a77ac07511943'
REDIRECT_URI = 'http://localhost:5000/callback'


# Define the base URL for the Withings API
BASE_URL = "https://wbsapi.withings.net"

# Example: Get user measurements
def get_measurements():
    url = f"{BASE_URL}/measure"
    headers = {
        'Authorization': f"Bearer {ACCESS_TOKEN}"
    }
    params = {
        'action': 'getmeas',
        'userid': USER_ID
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=4))
    else:
        print(f"Error: {response.status_code}, {response.text}")

# Example: Refresh the token
def refresh_access_token():
    url = "https://wbsapi.withings.net/v2/oauth2"
    data = {
        'action': 'requesttoken',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN
    }
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        new_tokens = response.json()['body']
        print("New Access Token:", new_tokens['access_token'])
        print("New Refresh Token:", new_tokens['refresh_token'])
    else:
        print(f"Error: {response.status_code}, {response.text}")

# Call the functions
get_measurements()
refresh_access_token()
