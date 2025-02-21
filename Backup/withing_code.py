import requests
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
import os

# This line allows HTTP for OAuth during local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Replace these with your actual client_id and client_secret
CLIENT_ID = '4c0441ed25b917cf01d8cccf9efd6b4def85e855e30bc66f91934cdb7bf5f848'
CLIENT_SECRET = 'e02317295a3b34119200877eeab1ac727cd06f8048c7855aab8a77ac07511943'
REDIRECT_URI = 'http://localhost:5000/callback'  # This should match what you registered with Withings

# Withings API URLs
AUTHORIZATION_BASE_URL = 'https://account.withings.com/oauth2_user/authorize2'
TOKEN_URL = 'https://account.withings.com/oauth2/token'

# Define the scope of access you need
scope = ['user.metrics']

# Step 1: Redirect the user to Withings for authorization
oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=scope)
authorization_url, state = oauth.authorization_url(AUTHORIZATION_BASE_URL)

print('Please go to this URL and authorize access:', authorization_url)

# Step 2: After authorization, Withings will redirect you to the redirect_uri with a code
# Copy that code from the URL and paste it below
authorization_response = input('Enter the full callback URL: ')

# Step 3: Exchange the authorization code for an access token
token = oauth.fetch_token(TOKEN_URL, authorization_response=authorization_response,
                          auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET))

print('Access token:', token)
