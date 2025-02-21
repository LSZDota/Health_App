# withings_auth.py

import requests
import json
import os
import webbrowser
import threading
from flask import Flask, request

# Replace these with your actual tokens and user ID
USER_ID = '38378503'
CLIENT_ID = '4c0441ed25b917cf01d8cccf9efd6b4def85e855e30bc66f91934cdb7bf5f848'
CLIENT_SECRET = 'e02317295a3b34119200877eeab1ac727cd06f8048c7855aab8a77ac07511943'
# REDIRECT_URI = 'http://localhost:5000/callback'
REDIRECT_URI = 'https://healthapp-7kifcu2bipx7vdwrgkpemh.streamlit.app/callback'
TOKENS_FILE = 'withings_tokens.json'

# Ensure the tokens file is in the saved_data directory
if not os.path.exists('saved_data'):
    os.makedirs('saved_data')

TOKENS_FILE_PATH = os.path.join('saved_data', TOKENS_FILE)

# Create an Event object to signal when authentication is complete
auth_complete = threading.Event()

# ----------------------------- OAuth Server -----------------------------

app = Flask(__name__)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        # Exchange the authorization code for tokens
        access_token, refresh_token = exchange_code_for_tokens(code)
        if access_token and refresh_token:
            save_tokens(access_token, refresh_token)
            # Signal that authentication is complete
            auth_complete.set()
            # Shut down the server
            shutdown_server()
            return 'Authorization successful! You can close this window.'
        else:
            # Signal that authentication failed
            auth_complete.set()
            # Shut down the server
            shutdown_server()
            return 'Failed to obtain tokens. Check the console for errors.'
    else:
        # Signal that authentication failed
        auth_complete.set()
        # Shut down the server
        shutdown_server()
        return 'Authorization code not found in the request.'

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()

def start_server():
    from threading import Thread
    server = Thread(target=app.run, kwargs={'port': 5000})
    server.start()
    return server

# ----------------------------- Token Functions -----------------------------

def exchange_code_for_tokens(auth_code):
    token_url = 'https://wbsapi.withings.net/v2/oauth2'
    token_data = {
        'action': 'requesttoken',
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
    }

    response = requests.post(token_url, data=token_data)
    response_json = response.json()

    if response_json.get('status') == 0:
        tokens = response_json['body']
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        print("Tokens obtained successfully.")
        return access_token, refresh_token
    else:
        print("Error obtaining tokens:", response_json)
        return None, None

def save_tokens(access_token, refresh_token):
    tokens = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    with open(TOKENS_FILE_PATH, 'w') as f:
        json.dump(tokens, f)
    print(f"Tokens saved to {TOKENS_FILE_PATH}")

# ----------------------------- Main Execution -----------------------------

def generate_auth_url():
   auth_url = (
       'https://account.withings.com/oauth2_user/authorize2?'
       f'response_type=code&client_id={CLIENT_ID}&state=withings_auth&'
       f'redirect_uri={REDIRECT_URI}&scope=user.metrics'
   )
   return auth_url

# def generate_auth_url():
#     auth_url = (
#         'https://account.withings.com/oauth2_user/authorize2?'
#         f'response_type=code&client_id={CLIENT_ID}&state=withings_auth&'
#         f'redirect_uri={REDIRECT_URI}&scope=user.metrics,user.activity,user.info,user.sleepevents'
#     )
#     return auth_url

if __name__ == '__main__':
    # For deployment on Streamlit Cloud, do not start a separate Flask server.
    # Instead, just generate and print the authorization URL.
    auth_url = generate_auth_url()
    print("Authorization URL:", auth_url)
    print("Please visit the URL above to authorize the app.")
    # On Streamlit Cloud, you will need to capture the authorization code from the URL parameters.
