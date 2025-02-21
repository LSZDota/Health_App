from requests_oauthlib import OAuth2Session
import requests


# OAuth2 credentials
client_id = '4c0441ed25b917cf01d8cccf9efd6b4def85e855e30bc66f91934cdb7bf5f848'
client_secret = 'e02317295a3b34119200877eeab1ac727cd06f8048c7855aab8a77ac07511943'
redirect_uri = 'http://localhost:5000/callback'
token_url = 'https://account.withings.com/oauth2/token'


# You should have the authorization code from the previous step
authorization_code = 'your_authorization_code'

# Create an OAuth2 session
withings = OAuth2Session(client_id, redirect_uri=redirect_uri)

# Data for the token exchange request
data = {
    'grant_type': 'authorization_code',
    'client_id': client_id,
    'client_secret': client_secret,
    'code': authorization_code,
    'redirect_uri': redirect_uri,
}

# Make the POST request to exchange the authorization code for an access token
response = requests.post(token_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})

# Print the full response for debugging
print("Response status code:", response.status_code)
print("Response headers:", response.headers)
print("Response text:", response.text)

# Attempt to parse the JSON response
try:
    token = response.json()
    print("Access Token:", token)
except ValueError as e:
    print("Error parsing token response:", e)