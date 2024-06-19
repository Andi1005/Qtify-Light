import datetime, random, os

from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import click

ID_DIGITS = 6

random.seed()
db = SQLAlchemy()


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(256), nullable=False)
    token_expires_at = db.Column(db.DateTime, nullable=False)
    refresh_token = db.Column(db.String(256), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    qr_code_path = db.Column(db.String(128), nullable=True)

    def __init__(self, access_token, token_expires_in, refresh_token):

        while True:
            id = random.randrange(int("1" * ID_DIGITS), int("9" * ID_DIGITS))
            existing_room = Room.query.filter_by(id=id).first()
            if existing_room is None:
                break

        token_expires_at = datetime.datetime.now() + datetime.timedelta(
            seconds=token_expires_in
        )
        super().__init__(
            id=id,
            access_token=access_token,
            token_expires_at=token_expires_at,
            refresh_token=refresh_token,
            expires_at=datetime.datetime.now() + current_app.config["ROOM_LIFESPAN"],
        )

    def __repr__(self):
        return f"<Room {self.id}>"


@click.command("tidy-db")
def tidy_db():
    """Goes through every Room in the database and deletes expired ones.
    This script is ment to run as a scheduled task.
    """

    counter = 0
    for room in Room.query.all():
        if room.expires_at < datetime.datetime.now():
            if room.qr_code_path is not None:
                os.remove(room.qr_code_path)

            db.session.delete(room)
            counter += 1

    db.session.commit()
    click.echo(f"{counter} rows deleted.")


@click.command("create-db")
def create_db():
    """Initiates the database"""
    db.create_all()
