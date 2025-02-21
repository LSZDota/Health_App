import requests

# Replace these with your actual tokens and user ID
USER_ID = '38378503'
CLIENT_ID = '4c0441ed25b917cf01d8cccf9efd6b4def85e855e30bc66f91934cdb7bf5f848'
CLIENT_SECRET = 'e02317295a3b34119200877eeab1ac727cd06f8048c7855aab8a77ac07511943'
REDIRECT_URI = 'http://localhost:5000/callback'
TOKENS_FILE = 'saved_data/withings_tokens.json'

auth_code = '2d5b262168abb5c3b63bd7fa2d3b0d0a91af899c'  # Replace with the code from auth_code.txt

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
print("Response status code:", response.status_code)
print("Response text:", response.text)
