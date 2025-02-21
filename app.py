import requests
from requests.auth import HTTPBasicAuth
import os

# Allow HTTP for development (not recommended for production)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Client credentials
CLIENT_ID = '4c0441ed25b917cf01d8cccf9efd6b4def85e855e30bc66f91934cdb7bf5f848'
CLIENT_SECRET = 'e02317295a3b34119200877eeab1ac727cd06f8048c7855aab8a77ac07511943'
REDIRECT_URI = 'http://localhost:5000/callback'
TOKEN_URL = 'https://account.withings.com/oauth2/token'

# Replace with the actual authorization code you receive
authorization_code = '52b9ad59e9fae8e46cb538d45efae642d2faac57'

# Build the request
token_request_data = {
    'grant_type': 'authorization_code',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'code': authorization_code,
    'redirect_uri': REDIRECT_URI
}

# Make the request
response = requests.post(TOKEN_URL, data=token_request_data, auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET))

# Debugging output
print("Response status code:", response.status_code)
print("Response headers:", response.headers)
print("Response text:", response.text)

# Parse the response if it's JSON
if response.headers.get('content-type') == 'application/json':
    token = response.json()
    print("Access Token:", token)
else:
    print("Unexpected response format - not JSON")
