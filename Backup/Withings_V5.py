from withings_api import WithingsApi, AuthScope
from withings_api.common import Credentials

# Replace these with your actual tokens and user ID
ACCESS_TOKEN = '83382eb735f76748e2baf64557ec1d38aeac29dd'
REFRESH_TOKEN = '74921286ad796bea2882f4e29237287e1b8fb65f'
USER_ID = '38378503'
CLIENT_ID = '4c0441ed25b917cf01d8cccf9efd6b4def85e855e30bc66f91934cdb7bf5f848'
CLIENT_SECRET = 'e02317295a3b34119200877eeab1ac727cd06f8048c7855aab8a77ac07511943'
REDIRECT_URI = 'http://localhost:5000/callback'


# Step 1: Create the credentials object
credentials = Credentials(
    access_token=ACCESS_TOKEN,
    token_expiry=10800,  # Typically returned by Withings in seconds
    token_type='Bearer',
    refresh_token=REFRESH_TOKEN,
    userid=USER_ID,
    client_id=CLIENT_ID,
    consumer_secret=CLIENT_SECRET,
)

# Step 2: Initialize the API client with the credentials
api = WithingsApi(credentials)

# Step 3: Fetch measurements
measurements = api.measure_get_meas()
for measuregrp in measurements.measuregrps:
    print(f"Date: {measuregrp.date}")
    for measure in measuregrp.measures:
        print(f"  - Type: {measure.type}, Value: {measure.value}")

# Refresh the token if necessary
new_credentials = api.refresh_token()
print("New Access Token:", new_credentials.access_token)
print("New Refresh Token:", new_credentials.refresh_token)