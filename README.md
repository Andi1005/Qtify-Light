# QTify-Light (Queue-tify)

A Flask webapp to easily add songs to the Spotify queue without needing the Spotify-controlling phone.
The website is currently running at [qtify.eu.pythonanywhere.com](https://qtify.eu.pythonanywhere.com/).
This project is an improved version of my old QTify app. It's simpler and more stabel.

## Installation and usage

1. Clone this Repository.
2. The config.py file needs to be customized.
3. In __init__.py the right config class has to be selected (config.Debug or config.Production).
4. Run the app from the Qtify-Light directory:
  > flask init-db
  > flask run

