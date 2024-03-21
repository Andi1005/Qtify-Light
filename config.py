import os, datetime

class BaseConfig:
    SECRET_KEY = ""

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
    INSTANCE_PATH = r"C:\Users\Andi\Code\Qtify-Light\instance"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(INSTANCE_PATH, "database.db")

    # Spotify Authorization
    CLIENT_ID = "bbe5ddb14c964b0aa88307badeb3e3a0"
    CLIENT_SECRET = "3a7cad52bf8440bc931f4a972a3cdf10"
    AUTH_SHOW_DIALOG = "true"

    ROOM_LIFESPAN = datetime.timedelta(hours=4)
    
class Production(BaseConfig):
    SECRET_KEY = "Change in Production"
    DEBUG = False
    TESTING = False

    PREFERRED_URL_SCHEME = "https"
    SERVER_NAME = "qtify.eu.pythonanywhere.com"
    APPLICATION_ROOT = "/"

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://qtify:password@qtify.mysql.eu.pythonanywhere-services.com/qtify$database"
    #SQLALCHEMY_DATABASE_URI = "mysql:///" + os.path.join(INSTANCE_PATH, "database.mysql") # without db driver

    CLIENT_ID = "bbe5ddb14c964b0aa88307badeb3e3a0"
    CLIENT_SECRET = "3a7cad52bf8440bc931f4a972a3cdf10"
    AUTH_SHOW_DIALOG = "true"

    ROOM_LIFESPAN = datetime.timedelta(hours=12)