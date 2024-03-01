import flask
import config


def create_app():
    app = flask.Flask(__name__)
    app.config.from_object(config.Debug)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import views
    app.register_blueprint(views.bp)

    return app

if __name__ == "__main__":
    create_app()
