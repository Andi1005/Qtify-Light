from functools import wraps
import base64
import datetime
from urllib.parse import urlencode
import secrets

import flask
from flask import current_app
import requests

from . import models


# Everything related to authorization and creating a new room
# QTify-Light uses Authorization Code to access and modify user data


bp = flask.Blueprint("auth", __name__)


def auth_required(func):
    """Checks if there is a valid id and saves the Room in flask.g.

    The wraped view is only executed if there is valid room id in the url.
    The coresponding room has to exist in the database and not be expired.
    If not, the user gets redirected to the index page with an error message.
    If the access token is expired, refresh_access_token is called.
    In the end, the valid models.Room object is saved in the flask.g context
    to be further used in the view function.

    Args:
        func (function): The view function that is being wraped

    Returns:
        Response: Either the response of the wraped view function or an error

    """

    @wraps(func)
    def decorated_function(*args, **kwargs):
        room_id = kwargs.get("room_id")
        if room_id is None:
            flask.flash(
                "Es wurde keine room id vom Client gesendet. (Error 400)",
                category="error",
            )
            return flask.redirect(flask.url_for("views.index"))

        room = models.Room.query.filter_by(id=room_id).first()
        if room is None:
            current_app.logger.info(f"Room not found with ID {room_id}.")
            flask.flash(
                "Der Raum wurde nicht auf dem Server gefunden. (Error 404)",
                category="error",
            )
            return flask.redirect(flask.url_for("views.index"))

        if room.expires_at < datetime.datetime.now():
            current_app.logger.info(f"Tried to use expired room {room}.")
            flask.flash("Der Raum ist abgelaufen (Error 410)", category="error")
            return flask.redirect(flask.url_for("views.index"))

        if room.token_expires_at < datetime.datetime.now():
            current_app.logger.info(f"Token expired in {room}.")
            refresh_access_token()

        flask.g.room = room

        return func(*args, **kwargs)

    return decorated_function


@bp.route("/auth")
def auth():
    """'/auth' endpoint. Redirects the user to spotify for authorization."""

    state = secrets.token_hex()
    flask.session["state"] = state
    url = "https://accounts.spotify.com/authorize/?"
    params = {
        "client_id": current_app.config["CLIENT_ID"],
        "response_type": "code",
        "redirect_uri": flask.url_for("auth.callback", _external=True),
        "state": state,
        "scope": " ".join(current_app.config["AUTH_SCOPE"]),
        "show_dialog": current_app.config["AUTH_SHOW_DIALOG"],
    }
    return flask.redirect(url + urlencode(params))


@bp.route("/auth/callback")
def callback():
    """'/auth/callback' endpoint. Requests an access token and creates a new room.

    This endpoint is only to be used by the Spotify auth services as
    callback from the auth view.
    If the user authorized the application, this function requests an access token
    from Spotify. This access token is saved in a new 'Room' database-entry with the
    request token and expiration date. If the authorization failed,
    the user is directed back to the index page (with an error message).

    URL Args:
        state: State parameter from previous request. Has to equal state in the session cookie
        code: Authorization code to request the access token
        error: The reason authorization failed if there was an error.

    Returns:
        Redirect: Redirects to the new room or the index page if there was an error
    """

    # Check state mismatch
    state = flask.session.get("state")
    if state is None or not state == flask.request.args.get("state"):
        current_app.logger.info(
            f"Authorization failed due to state mismatch ({state} and {flask.request.args.get('state')})"
        )
        flask.flash("Autorisierung fehlgeschlagen (Error 400)")
        return flask.redirect(flask.url_for("views.index"))

    # Check if authorization was unsuccessful
    code = flask.request.args.get("code")
    if code is None:
        error = flask.request.args.get("error")
        current_app.logger.info(f"Authorisation failed (From Spotify: {error})")
        flask.flash("Autorisierung fehlgeschlagen (Error 401)")
        return flask.redirect(flask.url_for("views.index"))

    url = "https://accounts.spotify.com/api/token"
    client_auth = (
        current_app.config["CLIENT_ID"] + ":" + current_app.config["CLIENT_SECRET"]
    )
    client_auth = base64.b64encode(client_auth.encode("ascii")).decode("ascii")
    headers = {
        "Authorization": "Basic " + client_auth,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": flask.url_for("auth.callback", _external=True),
    }

    response = requests.post(url, headers=headers, data=body)
    if not response.status_code == 200:
        current_app.logger.info(
            f"Authorisation failed while requesting access token (From Spotify: {response.content})"
        )
        
        flask.flash("Autorisierung fehlgeschlagen (Error 403)")
        return flask.redirect(flask.url_for("views.index"))

    response_data = response.json()
    new_room = models.Room(
        response_data["access_token"],
        response_data["expires_in"],
        response_data["refresh_token"],
    )
    models.db.session.add(new_room)
    models.db.session.commit()

    print(response_data["access_token"])

    current_app.logger.info(f"New room created {new_room}")

    return flask.redirect(flask.url_for("views.room", room_id=new_room.id))


def refresh_access_token(room: models.Room) -> None | Exception:
    """Requests a new access token with the refresh token from the Room model."""

    client_auth = (
        current_app.config["CLIENT_ID"] + ":" + current_app.config["CLIENT_SECRET"]
    )
    client_auth = base64.b64encode(client_auth.encode("ascii")).decode("ascii")
    headers = {
        "Authorization": "Basic " + client_auth,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    body = {
        "grant_type": "refresh_token",
        "refresh_token": room.refresh_token,
    }

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data=body,
        headers=headers,
    )

    if not response.status_code == 200:
        current_app.logger.error(
            f"Unexpected response while refreshing access token: {response.content}"
        )
        raise ValueError(
            f"Unexpected response while refreshing access token: {response.status_code}"
        )

    response_data = response.json()
    room.access_token = response_data["access_token"]
    room.refresh_token = response_data["refresh_token"]
    expires_in = datetime.timedelta(response_data["expires_in"])
    room.token_expires_at = datetime.datetime.now() + datetime.timedelta(
        seconds=expires_in
    )

    models.db.session.commit()

    current_app.logger.info(f"Refreshed access token for {room}")
