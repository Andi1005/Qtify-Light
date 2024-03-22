import os

import flask
import requests
import qrcode

from . import auth, models

bp = flask.Blueprint("views", __name__)

# For the "/auth" and "/auch/callback" route see auth.py

@bp.route("/")
def index():
    """Root endpoint with a short explanation and link to create a new room."""
    return flask.render_template("index.html")

@bp.route("/<room_id>", methods=["GET", "POST"])
@auth.auth_required
def room(room_id):
    """'/<room_id>' endpoint. You can search for songs and add them to the queue.

    If the request method is POST, the view validates the track-uri, checks if it
    is already in the queue and, if not, adds the track to the queue.
    In the case of an error, the user is redirected to the index page with an error
    messge.

    Args:
        room_id (int): Url parameter to access a Room entry in the database.
    """

    if flask.request.method == "POST":
        track_uri = flask.request.form.get("track-uri")
        if track_uri is None:
            flask.abort(400)

        response = requests.get(
            "https://api.spotify.com/v1/me/player/queue",
            headers={"Authorization": "Bearer " + flask.g.room.access_token,},
            )

        if response.status_code >= 400:
            flask.current_app.logger.error(
                f"Error while requesting queue: {response.content}")
            flask.flash(
                "Es ist ein Fehler mit Spotify aufgetreten (Error 500)",
                category="error")

        elif response.status_code == 200:
            response_data = response.json()
            for track in response_data["queue"]:
                if track["uri"] == track_uri:
                    flask.flash("Dieser Song ist schon in der Warteschlange.",
                        category="info")
                    return flask.render_template("room.html")

        response = requests.post(
            "https://api.spotify.com/v1/me/player/queue",
            params={"uri": track_uri,},
            headers={"Authorization": "Bearer " + flask.g.room.access_token,},
        )

        if response.status_code == 404:
            flask.flash(
                "Es wurde kein Gerät gefunden, dass Spotify abspielt.",
                category="error")

        elif response.status_code == 204:
            flask.current_app.logger.info(f"Added track to queue ({track_uri})")
            flask.flash("Song zur Warteschlange hinzugefügt.",
                category="info")

        elif response.status_code >= 400:
            return response.content

    return flask.render_template("room.html", room_id=room_id)

@bp.route("/<room_id>/search")
@auth.auth_required
def search(room_id):
    LIMIT = 10
    q = flask.request.args["q"]
    if len(q) == 0:
        flask.abort(400)

    page = flask.request.args.get("page", default=0, type=int)

    params = {
        "q": q,
        "type": "track",
        "market": "DE",
        "limit": LIMIT,
        "offset": LIMIT * page,
    }

    response = requests.get(
        "https://api.spotify.com/v1/search",
        params=params,
        headers={"Authorization": "Bearer " + flask.g.room.access_token,},
    )

    if response.status_code >= 400:
        print(flask.g.room.access_token)
        print(type(flask.g.room.access_token))
        flask.current_app.logger.error(response.content)
        return "Communication with Spotify failed", 500

    elif response.status_code == 200:
        response_data = response.json()
        search_result = []
        for track in response_data["tracks"]["items"]:
            search_result.append({
                "uri": track["uri"],
                "name": track["name"],
                "artist": ", ".join(artist["name"] for artist in track["artists"]),
                "image": track["album"]["images"][-1]["url"] # Url to the image with the lowest resolution
            })

    return flask.render_template("search-result.html", tracks=search_result)

@bp.route("/<room_id>/join")
@auth.auth_required
def join(room_id):
    url = flask.url_for("views.room", room_id=room_id, _external=True)

    room = models.Room.query.get(room_id)
    if room.qr_code_path is None:
        filename = f"qrcode_{room_id}.png"
        qr_code_path = os.path.join(flask.current_app.instance_path, "qr-codes", filename)

        qr_code = qrcode.make(url)
        qr_code.save(qr_code_path)

        room.qr_code_path = qr_code_path
        models.db.session.commit()

    return flask.render_template("join.html", room_id=room_id)

@bp.route("/qr-code/<room_id>")
@auth.auth_required
def qr_code(room_id):
    return flask.send_file(flask.g.room.qr_code_path, mimetype="image/png")

