import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

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

# Plot the data
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
    
    # Sort the data by date
    dates, values = zip(*sorted(zip(dates, values)))
    
    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(dates, values, marker='o')
    plt.title(f'{measure_name} Over Time')
    plt.xlabel('Date')
    plt.ylabel(measure_name)
    plt.grid(True)
    plt.show()

# Set up tkinter GUI
def create_button(root, text, measure_type, measure_name):
    button = tk.Button(root, text=text, command=lambda: plot_measurements(measure_type, measure_name))
    button.pack(pady=5)

root = tk.Tk()
root.title("Withings Data Visualization")

# Create buttons for each type of measurement
create_button(root, "Weight (kg)", 1, "Weight (kg)")
create_button(root, "Fat Ratio (%)", 6, "Fat Ratio (%)")
create_button(root, "Fat-Free Mass (kg)", 5, "Fat-Free Mass (kg)")
create_button(root, "Fat Mass Weight (kg)", 8, "Fat Mass Weight (kg)")
create_button(root, "Muscle Mass (kg)", 76, "Muscle Mass (kg)")
create_button(root, "Hydration (kg)", 77, "Hydration (kg)")
create_button(root, "Bone Mass (kg)", 88, "Bone Mass (kg)")
create_button(root, "Visceral Fat Level", 170, "Visceral Fat Level")
create_button(root, "Body Score (units)", 226, "Body Score (units)")

root.mainloop()