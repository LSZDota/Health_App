from requests_oauthlib import OAuth2Session
import os
import webbrowser

# OAuth2 credentials
client_id = '4c0441ed25b917cf01d8cccf9efd6b4def85e855e30bc66f91934cdb7bf5f848'
client_secret = 'e02317295a3b34119200877eeab1ac727cd06f8048c7855aab8a77ac07511943'
redirect_uri = 'http://localhost:5000/callback'
authorization_base_url = 'https://account.withings.com/oauth2_user/authorize2'
token_url = 'https://account.withings.com/oauth2/token'

# Scopes define the permissions that the application is requesting
scope = ['user.metrics']  # Example scope, adjust based on what you need

# Disable SSL verification for local development (not recommended for production)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Create an OAuth2 session
withings = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)

# Get the authorization URL and state
authorization_url, state = withings.authorization_url(authorization_base_url)

# Open the URL in the browser
print(f'Please go to {authorization_url} and authorize access.')
webbrowser.open(authorization_url)

# Get the authorization response URL from the user
redirect_response = input('Paste the full redirect URL here: ')

# Fetch the access token
token = withings.fetch_token(token_url, authorization_response=redirect_response, client_secret=client_secret)

# Display the token
print('Access token:', token)
