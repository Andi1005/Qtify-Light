class BaseConfig:
    SECRET_KEY = ""

class Debug(BaseConfig):
    SECRET_KEY = "Debug"
    DEBUG = True
    BASE_URL = "http://localhost:5000/"

    # Spotify Authorization
    #CLIENT_ID = "4399653f3dd8486eacb4fd2b1f29c838"
    CLIENT_ID = "bbe5ddb14c964b0aa88307badeb3e3a0"
    CLIENT_KEY = "4fca974e0df54b98905514c4bd443894"
    AUTH_SCOPE = ["user-read-playback-state"]
    AUTH_SHOW_DIALOG = "true"
    AUTH_STATE = "Debug"
    