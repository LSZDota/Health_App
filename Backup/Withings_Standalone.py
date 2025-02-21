import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime

# Replace these with your actual tokens and user ID
USER_ID = '38378503'
CLIENT_ID = '4c0441ed25b917cf01d8cccf9efd6b4def85e855e30bc66f91934cdb7bf5f848'
CLIENT_SECRET = 'e02317295a3b34119200877eeab1ac727cd06f8048c7855aab8a77ac07511943'
REDIRECT_URI = 'http://localhost:5000/callback'
REFRESH_TOKEN = '74921286ad796bea2882f4e29237287e1b8fb65f'  # Replace with your initial refresh token

# Fetch new tokens
def refresh_tokens():
    token_url = 'https://wbsapi.withings.net/v2/oauth2'
    token_data = {
        'action': 'requesttoken',
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
    }
    
    response = requests.post(token_url, data=token_data)
    tokens = response.json()['body']
    return tokens['access_token'], tokens['refresh_token']

# Get the latest tokens
access_token, refresh_token = refresh_tokens()

# Fetch measurements from Withings API
def fetch_measurements(measure_type):
    url = 'https://wbsapi.withings.net/measure'
    params = {
        'action': 'getmeas',
        'access_token': access_token,
        'meastype': measure_type,
        'category': 1
    }
    
    response = requests.get(url, params=params)
    data = response.json()['body']['measuregrps']
    return data

# Save data to a JSON file
def save_measurements_to_json(measure_type, measure_name):
    data = fetch_measurements(measure_type)
    for entry in data:
        entry['date'] = datetime.utcfromtimestamp(entry['date']).isoformat()
    
    # Save to a JSON file
    with open(f'{measure_name.lower().replace(" ", "_")}_data.json', 'w') as f:
        json.dump(data, f, indent=4)

# Save measurements for each type
save_measurements_to_json(1, "Weight (kg)")
save_measurements_to_json(6, "Fat Ratio (%)")
save_measurements_to_json(5, "Fat-Free Mass (kg)")
save_measurements_to_json(8, "Fat Mass Weight (kg)")
save_measurements_to_json(76, "Muscle Mass (kg)")
save_measurements_to_json(77, "Hydration (kg)")
save_measurements_to_json(88, "Bone Mass (kg)")
save_measurements_to_json(170, "Visceral Fat Level")
save_measurements_to_json(226, "Body Score (units)")

print("Data saved successfully.")
