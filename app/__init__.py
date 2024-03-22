import os

import flask

import config


def create_app():
    app = flask.Flask(__name__)
    app.config.from_object(config.Debug)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import models

    models.db.init_app(app)
    app.cli.add_command(models.create_db)
    app.cli.add_command(models.tidy_db)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import views

    app.register_blueprint(views.bp)

    return app


if __name__ == "__main__":
    app = create_app()
