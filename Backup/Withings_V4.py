import logging
from withings_api import WithingsAuth, WithingsApi, AuthScope

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Replace these with your values
CLIENT_ID = '4c0441ed25b917cf01d8cccf9efd6b4def85e855e30bc66f91934cdb7bf5f848'
CLIENT_SECRET = 'e02317295a3b34119200877eeab1ac727cd06f8048c7855aab8a77ac07511943'
REDIRECT_URI = 'http://localhost:5000/callback'

# Step 1: Create the authentication URL
auth = WithingsAuth(
    client_id=CLIENT_ID,
    consumer_secret=CLIENT_SECRET,
    callback_uri=REDIRECT_URI,
    scope=(AuthScope.USER_INFO, AuthScope.USER_METRICS)  # Add any other scopes you need
)

authorize_url = auth.get_authorize_url()
print("Go to the following URL and authorize the app:", authorize_url)

# Step 2: After the user authorizes the app, they will be redirected to your REDIRECT_URI
# with a 'code' URL parameter. You'll use this code to get an access token.
authorization_code = input("Enter the authorization code from the callback URL: ")

# Step 3: Fetch the credentials (including access token, refresh token, and user ID)
try:
    credentials = auth.get_credentials(authorization_code)
    # Extract and print the tokens and user ID
    access_token = credentials.access_token
    refresh_token = credentials.refresh_token
    user_id = credentials.userid

    print("Access Token:", access_token)
    print("Refresh Token:", refresh_token)
    print("User ID:", user_id)

    # Step 4: Use the access token to create an API instance
    api = WithingsApi(credentials)

    # Step 5: Fetch some data (e.g., measurements)
    measurements = api.measure_get_meas()
    for measure in measurements.measuregrps:
        print("Date:", measure.date)
        for m in measure.measures:
            print(f"  - Type: {m.type}, Value: {m.value}")

except Exception as e:
    print(f"An error occurred: {e}")
