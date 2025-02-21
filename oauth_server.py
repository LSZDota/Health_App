# oauth_server.py
from flask import Flask, request

app = Flask(__name__)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        with open('saved_data/auth_code.txt', 'w') as f:
            f.write(code)
        return 'Authorization code received! You can close this window.'
    else:
        return 'Error: Authorization code not found.'

if __name__ == '__main__':
    app.run(port=5000)
