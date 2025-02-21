# Save tokens to file
def save_tokens(access_token, refresh_token):
    tokens = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    with open('saved_data/withings_tokens.json', 'w') as f:
        json.dump(tokens, f)



# Load tokens from file
def load_tokens():
    if os.path.exists('saved_data/withings_tokens.json'):
        with open('saved_data/withings_tokens.json', 'r') as f:
            tokens = json.load(f)
            return tokens.get('access_token'), tokens.get('refresh_token')
    else:
        return None, None


response = requests.post(token_url, data=token_data)
response_json = response.json()

if response_json.get('status') == 0:
    tokens = response_json['body']
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']
    save_tokens(access_token, refresh_token)
    print("Tokens saved successfully.")
else:
    print("Error obtaining tokens:", response_json)
