from flask import Flask, render_template, jsonify
import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime
import io
import base64
import time

app = Flask(__name__)

# Replace these with your actual tokens and user ID
USER_ID = '38378503'
CLIENT_ID = '4c0441ed25b917cf01d8cccf9efd6b4def85e855e30bc66f91934cdb7bf5f848'
CLIENT_SECRET = 'e02317295a3b34119200877eeab1ac727cd06f8048c7855aab8a77ac07511943'
REDIRECT_URI = 'http://localhost:5000/callback'
REFRESH_TOKEN = '74921286ad796bea2882f4e29237287e1b8fb65f'

# Fetch new tokens with retry logic
def refresh_tokens():
    token_url = 'https://wbsapi.withings.net/v2/oauth2'
    token_data = {
        'action': 'requesttoken',
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
    }
    
    for attempt in range(3):  # Retry up to 3 times
        response = requests.post(token_url, data=token_data)
        print("Response status code:", response.status_code)
        print("Response text:", response.text)
        
        if response.status_code == 200:
            response_json = response.json()
            if response_json['status'] == 0:
                tokens = response_json['body']
                return tokens['access_token'], tokens['refresh_token']
            elif response_json['status'] == 601:
                wait_seconds = response_json['body']['wait_seconds']
                print(f"Waiting for {wait_seconds} seconds before retrying...")
                time.sleep(wait_seconds)
            else:
                raise ValueError(f"Unexpected response status: {response_json['status']}")
    
    raise ValueError("Failed to retrieve tokens after retries. Response: " + response.text)

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

# Plot the data and return the plot as a base64 string
def plot_measurements(measure_type, measure_name):
    data = fetch_measurements(measure_type)
    dates = []
    values = []
    
    for entry in data:
        for measure in entry['measures']:
            if measure['type'] == measure_type:
                date = datetime.utcfromtimestamp(entry['date'])
                value = measure['value'] * (10 ** measure['unit'])
                dates.append(date)
                values.append(value)
    
    if dates and values:
        # Sort the data by date
        dates, values = zip(*sorted(zip(dates, values)))
        
        # Plotting
        plt.figure(figsize=(10, 5))
        plt.plot(dates, values, marker='o')
        plt.title(f'{measure_name} Over Time')
        plt.xlabel('Date')
        plt.ylabel(measure_name)
        plt.grid(True)

        # Save the plot to a PNG image in memory
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)

        # Encode the image as base64 to send to the frontend
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')

        return plot_url
    else:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot/<measure_type>/<measure_name>')
def plot(measure_type, measure_name):
    measure_type = int(measure_type)
    plot_url = plot_measurements(measure_type, measure_name)
    if plot_url:
        return jsonify({'status': 'success', 'plot_url': plot_url})
    else:
        return jsonify({'status': 'error', 'message': 'No data available'})

if __name__ == '__main__':
    app.run(debug=True)
