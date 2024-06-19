import os
from socket import gethostname

import flask

import config


def create_app():
    app = flask.Flask(__name__)
    app.config.from_object(config.Production)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(os.path.join(app.instance_path, "qr-codes"), exist_ok=True)

    from . import models

    models.db.init_app(app)
    app.cli.add_command(models.create_db)
    app.cli.add_command(models.tidy_db)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import views

    app.register_blueprint(views.bp)

    return app


app = create_app()

if __name__ == "__main__":
    if "liveconsole" not in gethostname():
        app.run()
