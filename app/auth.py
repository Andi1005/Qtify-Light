from urllib.parse import urlencode
import base64

import flask
from flask import current_app
import requests

bp = flask.Blueprint("auth", __name__)


def generate_client_auth(client_id, client_secret):
    message = f"{client_id}:{client_secret}"
    message_bytes = message.encode("ascii")
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode("ascii")

    return base64_message

@bp.route("/auth")
def auth():
    url = "https://accounts.spotify.com/authorize/?"
    params = {
        "client_id": current_app.config["CLIENT_ID"],
        "response_type": "code",
        "redirect_uri": current_app.config["BASE_URL"],
		"state": current_app.config["AUTH_STATE"],
        "scope": " ".join(current_app.config["AUTH_SCOPE"]),
        "show_dialog": current_app.config["AUTH_SHOW_DIALOG"],
    }
    return flask.redirect(url + urlencode(params))

@bp.route("/auth/callback")
def auth_callback():
    state = flask.request.args.get("state")

    if not state == current_app.config["AUTH_STATE"]:
        return "Error: state mismatch" # TODO: replace in production
    
    code = flask.request.args.get("code")
    if code is None:
        error = flask.request.args.get("error")
        return "Error from Spotify: " + error
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": generate_client_auth(),
        "Content-Type": " application/x-www-form-urlencoded"
    }
    body = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": current_app.config["BASE_URL"],
    }

    response = requests.post(url, headers=headers, data=body)
    if not response.status_code == 200:
        return "Error: unexpected anwer from /api/token"
    
    

    # response = response.json()



