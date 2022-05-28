"""
    Class for the Spotify API 
"""
from __future__ import annotations
from time import time
from typing import Any

from requests import request, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from credentials_info import SECRET_CLIENT_ID, SECRET_KEY
from flask import url_for, request

# Global Variable for the SESSION_TOKEN
SESSION_TOKEN = "session-token"
VALID_ROUTES = ["home_page", "login_page",
                "authorization_page", "tracks_page", "albums_page"]
TOKEN_INFO = "session-token"


class SpotifyAPI:
    """
    A SpotifyAPI Object that will include the Authorization, extracting songs, 
    ablums, and other useful information. 

    Instance Variables: 
        - auth_manager: SpotifyOAuth object by creating a brand new one every time.  
        - client_id: Unique ID obtained from the developer tools on https://developer.spotify.com/
        - client_secret_key: Unqiue secret key obtained from the developer tools on https://developer.spotify.com/
        - session_token: refers to the current session key. 
        - redirect_url: the route to be redirected to. 
        - scope: the data that needs to be requested. 
    """
    auth_manager: Any
    client_id: str
    client_secret_key: str
    session_token: str
    redirect_url: str
    scope: str
    session

    def __init__(self) -> None:
        self.auth_manager = None
        self.client_id = SECRET_CLIENT_ID
        self.client_secret_key = SECRET_KEY
        self.redirect_url = ""
        self.scope = ""
        self.session_token = ""

    def create_spotify_oauth(self, redirect_to_url: str, request_for: str) -> None:
        """
        Creates a SpotifyOAuth Object that takes in the redirect route and the data to be requested.

            Preconditions: 
                - redirected_to_url must be a valid route
        """

        if redirect_to_url in VALID_ROUTES:
            self.auth_manager = SpotifyOAuth(client_id=self.client_id,
                                             client_secret=self.client_secret_key,
                                             redirect_uri=url_for(
                                                 redirect_to_url, _external=True),
                                             scope=request_for)
        else:
            raise ValueError

    def generate_new_session(self) -> None:
        """
        Creates a new session for the user.
        """
        req_code = request.args.get('code')
        self.session_token = self.auth_manager.get_access_token(req_code)
        session[TOKEN_INFO] = self.session_token

    def check_token(self) -> session:
        """
        Fetches the session's token then compares with token's expire time. 
        If token is expired then generate a new one.
        """
        self.session_token = session.get(TOKEN_INFO, None)
        #  "if info" == "not info" negation
        if not self.session_token:
            raise "Exception to be raised"

        # Check if the token is expired
        current_time = int(time.time())
        expires = self.session_token['expires_at'] - current_time < 60
        if expires:
            # Create a new token
            sp_oauth = SpotifyAPI()
            sp_oauth.create_spotify_oauth(
                "authorization_page", "user-library-read")
            self.session_token = sp_oauth.auth_manager.refresh_access_token(
                self.session_info['refresh_token'])
        return self.session_token


class SessionError(Exception):
    """
    Exception raised when session's token is None
    
    Instance Attributes: 
        - message: message to be raised. Defaulted. 
    """

    message: str

    def __init__(self, msg="Error Occured during the session's token extraction") -> None:
        self.message = msg
        super().__init__(self.message)
