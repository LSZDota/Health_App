import os
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Replace these with your actual tokens and user ID
USER_ID = '38378503'
CLIENT_ID = '4c0441ed25b917cf01d8cccf9efd6b4def85e855e30bc66f91934cdb7bf5f848'
CLIENT_SECRET = 'e02317295a3b34119200877eeab1ac727cd06f8048c7855aab8a77ac07511943'
REDIRECT_URI = 'http://localhost:5000/callback'
REFRESH_TOKEN = '74921286ad796bea2882f4e29237287e1b8fb65f'  # Replace with your initial refresh token

# Function to refresh the access token
def refresh_access_token(refresh_token):
    token_url = "https://wbsapi.withings.net/v2/oauth2"
    data = {
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token,
        'action': 'requesttoken'
    }
    response = requests.post(token_url, data=data)
    response_data = response.json()

    if response_data['status'] != 0:
        raise Exception(f"Failed to refresh token: {response_data}")

    new_access_token = response_data['body']['access_token']
    new_refresh_token = response_data['body']['refresh_token']

    # Store the new tokens in environment variables or a secure location
    os.environ['WITHINGS_ACCESS_TOKEN'] = new_access_token
    os.environ['WITHINGS_REFRESH_TOKEN'] = new_refresh_token

    return new_access_token, new_refresh_token

# Function to get the API client with the latest tokens
def get_access_token():
    access_token = os.getenv('WITHINGS_ACCESS_TOKEN', None)
    refresh_token = os.getenv('WITHINGS_REFRESH_TOKEN', REFRESH_TOKEN)

    if not access_token:
        access_token, refresh_token = refresh_access_token(refresh_token)

    return access_token

# Function to fetch measurements
def fetch_measurements():
    access_token = get_access_token()

    url = "https://wbsapi.withings.net/measure"
    params = {
        'action': 'getmeas',
        'access_token': access_token,
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] != 0:
        raise Exception(f"Failed to fetch data: {data}")

    measurements = data['body']['measuregrps']
    parsed_data = []

    for measuregrp in measurements:
        for measure in measuregrp['measures']:
            parsed_data.append({
                'date': datetime.utcfromtimestamp(measuregrp['date']).strftime('%Y-%m-%d %H:%M:%S'),
                'type': measure['type'],
                'value': measure['value'] * (10 ** measure['unit']),
                'unit': measure['unit'],
                'model': measuregrp.get('model', 'Unknown')
            })

    # Store the data in a Pandas DataFrame
    df = pd.DataFrame(parsed_data)
    return df

# Function to plot data
def plot_data(df, measure_type):
    filtered_df = df[df['type'] == measure_type]

    # Sort the data by date in ascending order
    filtered_df['date'] = pd.to_datetime(filtered_df['date'])
    filtered_df = filtered_df.sort_values(by='date')

    plt.figure(figsize=(10, 5))
    plt.plot(filtered_df['date'], filtered_df['value'], marker='o')
    plt.title(f'{measure_type} over Time')
    plt.xlabel('Date')
    plt.ylabel('Weight (kg)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Fetch and store the data
    df = fetch_measurements()

    # Example of plotting the weight data (assuming '1' corresponds to weight)
    plot_data(df, 1)  # Replace '1' with the correct measure type for weight

    # If you want to save the DataFrame to a file (e.g., CSV)
    df.to_csv('withings_data.csv', index=False)