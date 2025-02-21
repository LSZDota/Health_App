# withings_smartwatch_app.py

import streamlit as st
import requests
import json
import os
import subprocess  # Add this import
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKENS_FILE_PATH = os.path.join(SCRIPT_DIR, 'saved_data', 'withings_tokens.json')

# Load CLIENT_ID and CLIENT_SECRET from withings_auth.py or config.py
CLIENT_ID = '4c0441ed25b917cf01d8cccf9efd6b4def85e855e30bc66f91934cdb7bf5f848'
CLIENT_SECRET = 'e02317295a3b34119200877eeab1ac727cd06f8048c7855aab8a77ac07511943'

def run_app():
    st.subheader("Withings SmartWatch Data Visualization")

    # Add a button to re-authenticate
    if st.button("Re-authenticate with Withings"):
        # Run withings_auth.py as a subprocess
        subprocess.Popen(['python', 'withings_auth.py'])
        st.info("Please complete the authentication in the opened browser window.")
        st.info("After completing authentication, click 'Check for Tokens'.")

    # Add a button to check for tokens
    if st.button("Check for Tokens"):
        st.experimental_rerun()

    # Check if tokens are available
    if os.path.exists(TOKENS_FILE_PATH):
        # Load tokens
        with open(TOKENS_FILE_PATH, 'r') as f:
            tokens = json.load(f)
            access_token = tokens.get('access_token')
            refresh_token = tokens.get('refresh_token')

        # Proceed to fetch and plot data
        data_type = st.selectbox("Choose data to visualize", ["Activity", "Heart Rate", "Sleep"])

        if st.button("Fetch and Plot Data"):
            if data_type == "Activity":
                fetch_and_plot_activity_data(access_token, refresh_token)
            elif data_type == "Heart Rate":
                fetch_and_plot_heart_rate_data(access_token, refresh_token)
            elif data_type == "Sleep":
                fetch_and_plot_sleep_data(access_token, refresh_token)
    else:
        st.warning("No tokens found. Please click 'Re-authenticate with Withings' to authenticate.")


def refresh_access_token(refresh_token):
    token_url = 'https://wbsapi.withings.net/v2/oauth2'
    token_data = {
        'action': 'requesttoken',
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token,
    }

    response = requests.post(token_url, data=token_data)
    response_json = response.json()

    if response_json.get('status') == 0:
        tokens = response_json['body']
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        save_tokens(access_token, refresh_token)
        return access_token, refresh_token
    else:
        st.error(f"Error refreshing tokens: {response_json}")
        return None, None

def save_tokens(access_token, refresh_token):
    tokens = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    with open(TOKENS_FILE_PATH, 'w') as f:
        json.dump(tokens, f)
    print(f"Tokens saved to {TOKENS_FILE_PATH}")

def fetch_and_plot_activity_data(access_token, refresh_token):
    # Define date range
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)  # Last 30 days

    activities = fetch_activity_data(access_token, start_date, end_date)

    # If access token expired, refresh it
    if activities is None:
        st.info("Refreshing access token...")
        access_token, refresh_token = refresh_access_token(refresh_token)
        if access_token:
            activities = fetch_activity_data(access_token, start_date, end_date)
        else:
            st.error("Failed to refresh access token.")
            return

    if activities:
        df = pd.DataFrame(activities)
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values('date', inplace=True)

        st.subheader("Steps Over Time")
        fig_steps = go.Figure()
        fig_steps.add_trace(go.Scatter(x=df['date'], y=df['steps'], mode='lines+markers', name='Steps'))
        fig_steps.update_layout(title='Daily Steps', xaxis_title='Date', yaxis_title='Number of Steps')
        st.plotly_chart(fig_steps, use_container_width=True)

        st.subheader("Calories Over Time")
        fig_calories = go.Figure()
        fig_calories.add_trace(go.Scatter(x=df['date'], y=df['calories'], mode='lines+markers', name='Calories'))
        fig_calories.update_layout(title='Daily Calories Burned', xaxis_title='Date', yaxis_title='Calories')
        st.plotly_chart(fig_calories, use_container_width=True)
    else:
        st.write("No activity data available for the selected period.")

def fetch_activity_data(access_token, start_date, end_date):
    url = 'https://wbsapi.withings.net/v2/measure'
    params = {
        'action': 'getactivity',
        'access_token': access_token,
        'startdateymd': start_date.strftime('%Y-%m-%d'),
        'enddateymd': end_date.strftime('%Y-%m-%d'),
        'data_fields': 'steps,distance,elevation,calories,active'
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data.get('status') == 0:
        activities = data['body']['activities']
        return activities
    elif data.get('status') == 401:
        # Access token expired
        return None
    else:
        st.error(f"Error fetching activity data: {data.get('error')}")
        return []

def fetch_and_plot_heart_rate_data(access_token, refresh_token):
    # Define date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)  # Last 24 hours

    heart_rate_data = fetch_heart_rate_data(access_token, start_date, end_date)

    # If access token expired, refresh it
    if heart_rate_data is None:
        st.info("Refreshing access token...")
        access_token, refresh_token = refresh_access_token(refresh_token)
        if access_token:
            heart_rate_data = fetch_heart_rate_data(access_token, start_date, end_date)
        else:
            st.error("Failed to refresh access token.")
            return

    if heart_rate_data:
        df = pd.DataFrame(heart_rate_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.sort_values('timestamp', inplace=True)

        st.subheader("Heart Rate Over Last 24 Hours")
        fig_hr = go.Figure()
        fig_hr.add_trace(go.Scatter(x=df['timestamp'], y=df['heart_rate'], mode='lines', name='Heart Rate'))
        fig_hr.update_layout(title='Heart Rate', xaxis_title='Time', yaxis_title='BPM')
        st.plotly_chart(fig_hr, use_container_width=True)
    else:
        st.write("No heart rate data available for the selected period.")

def fetch_heart_rate_data(access_token, start_date, end_date):
    url = 'https://wbsapi.withings.net/v2/measure'
    params = {
        'action': 'getintradayactivity',
        'access_token': access_token,
        'startdate': int(start_date.timestamp()),
        'enddate': int(end_date.timestamp()),
        'data_fields': 'heart_rate'
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data.get('status') == 0:
        series = data['body']['series']
        heart_rate_data = [{'timestamp': int(timestamp), 'heart_rate': entry.get('heart_rate')} for timestamp, entry in series.items()]
        return heart_rate_data
    elif data.get('status') == 401:
        # Access token expired
        return None
    else:
        st.error(f"Error fetching heart rate data: {data.get('error')}")
        return []

def fetch_and_plot_sleep_data(access_token, refresh_token):
    # Define date range
    end_date = datetime.today()
    start_date = end_date - timedelta(days=7)  # Last 7 days

    sleep_data = fetch_sleep_data(access_token, start_date, end_date)

    # If access token expired, refresh it
    if sleep_data is None:
        st.info("Refreshing access token...")
        access_token, refresh_token = refresh_access_token(refresh_token)
        if access_token:
            sleep_data = fetch_sleep_data(access_token, start_date, end_date)
        else:
            st.error("Failed to refresh access token.")
            return

    if sleep_data:
        df = pd.DataFrame(sleep_data)
        df['date'] = pd.to_datetime(df['date'])
        df['sleep_duration'] = df['data'].apply(lambda x: x['total_sleep_time'] / 3600)  # Convert seconds to hours

        st.subheader("Sleep Duration Over Last 7 Days")
        fig_sleep = go.Figure()
        fig_sleep.add_trace(go.Bar(x=df['date'], y=df['sleep_duration'], name='Sleep Duration'))
        fig_sleep.update_layout(title='Sleep Duration', xaxis_title='Date', yaxis_title='Hours')
        st.plotly_chart(fig_sleep, use_container_width=True)
    else:
        st.write("No sleep data available for the selected period.")

def fetch_sleep_data(access_token, start_date, end_date):
    url = 'https://wbsapi.withings.net/v2/sleep'
    params = {
        'action': 'getsummary',
        'access_token': access_token,
        'startdateymd': start_date.strftime('%Y-%m-%d'),
        'enddateymd': end_date.strftime('%Y-%m-%d'),
        'data_fields': 'total_sleep_time'
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data.get('status') == 0:
        series = data['body']['series']
        return series
    elif data.get('status') == 401:
        # Access token expired
        return None
    else:
        st.error(f"Error fetching sleep data: {data.get('error')}")
        return []

