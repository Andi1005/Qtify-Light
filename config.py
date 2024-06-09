import os, datetime


class BaseConfig:
    SECRET_KEY = "Replace in Production"

    AUTH_SCOPE = [
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-read-currently-playing",
    ]


class Debug(BaseConfig):
    # Flask
    SECRET_KEY = "Debug"
    DEBUG = True
    TESTING = False

    PREFERRED_URL_SCHEME = "http"
    SERVER_NAME = "127.0.0.1:5000"
    APPLICATION_ROOT = "/"

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"

    # Spotify Authorization
    CLIENT_ID = "bbe5ddb14c964b0aa88307badeb3e3a0"
    CLIENT_SECRET = "Replace in Production"
    AUTH_SHOW_DIALOG = "true"

    ROOM_LIFESPAN = datetime.timedelta(hours=4)


class Production(BaseConfig):
    SECRET_KEY = "Replace in Production"
    DEBUG = False
    TESTING = False

    PREFERRED_URL_SCHEME = "https"
    SERVER_NAME = "qtify.eu.pythonanywhere.com"
    APPLICATION_ROOT = "/"

    _DATABASE_PW = "Replace in Production"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://QTify:{_DATABASE_PW}@QTify.mysql.eu.pythonanywhere-services.com/QTify$default"

    CLIENT_ID = "bbe5ddb14c964b0aa88307badeb3e3a0"
    CLIENT_SECRET = "Replace in Production"
    AUTH_SHOW_DIALOG = "true"

    ROOM_LIFESPAN = datetime.timedelta(hours=12)
