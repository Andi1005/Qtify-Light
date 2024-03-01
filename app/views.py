import flask

bp = flask.Blueprint("views", __name__)

# For the "/auth" route see auth.py

@bp.route("/")
def index():
    return flask.render_template("index.html")

@bp.route("/<pin>", methods=["GET", "POST"])
def room(pin):
    if flask.request.method == "POST":
        # Add to queue
        pass

    elif flask.request.method == "GET":
        return flask.render_template("room.html")

@bp.route("/<pin>/search")
def search():
    pass
    # return search results