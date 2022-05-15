"""
    Login Spotify OAuth
"""
import spotify
from spotipy.oauth2 import SpotifyOAuth
from flask import url_for


def make_spotify_oauth(secret_client_id: str, secret_key: str):
    """
    Takes in Two parameters: secret_client, and secret_key that are associated with
    the app on the spotify developer build.
    """
    return SpotifyOAuth(client_id=secret_client_id,
                        client_secret=secret_key,
                        redirect_uri=url_for('authorization_page', _external=True),
                        scope="user-library-read")
