""" Flask App"""
from flask import Flask
from media.credentials_info import SESSION_SECRET_KEY
# from spotipy import SpotifyOAuth

app = Flask(__name__)
# sp = SpotifyOAuth
app.config['SESSION_COOKIE_NAME'] = "Ansh's Session"
app.secret_key = SESSION_SECRET_KEY


from media import routes
