# """
#     Class for the Spotify API
# """
# from __future__ import annotations
# from typing import Any
#
# import spotipy
# from spotipy.oauth2 import SpotifyOAuth
# from media.credentials_info import SECRET_CLIENT_ID, SECRET_KEY
# from flask import url_for, request, session
#
# # Global Variable for the SESSION_TOKEN
#
#
# class SpotifyAPI:
#     """
#     A SpotifyAPI Object that will include the Authorization, extracting songs,
#     albums, and other useful information.
#
#     Instance Variables:
#         - auth_manager: SpotifyOAuth object by creating a brand new one every time.
#         - client_id: Unique ID obtained from the developer tools on https://developer.spotify.com/
#         - client_secret_key: Unique secret key obtained from the developer tools on https://developer.spotify.com/
#         - redirect_url: the route to be redirected to.
#         - scope: the data that needs to be requested.
#     """
#     auth_manager: Any
#     client_id: str
#     client_secret_key: str
#     redirect_url: str
#     scope: str
#
#     def __init__(self) -> None:
#         self.auth_manager = None
#         self.client_id = SECRET_CLIENT_ID
#         self.client_secret_key = SECRET_KEY
#         self.redirect_url = ""
#         self.scope = ""
#
#     def create_spotify_oauth(self, redirect_to_url: str, request_for: str) -> None:
#         """
#         Creates a SpotifyOAuth Object that takes in the redirect route and the data to be requested.
#
#             Preconditions:
#                 - redirected_to_url must be a valid route
#         """
#
#         self.auth_manager = SpotifyOAuth(client_id=self.client_id,
#                                          client_secret=self.client_secret_key,
#                                          redirect_uri=url_for(
#                                              redirect_to_url, _external=True),
#                                          scope=request_for)
#
#     # def generate_new_session(self) -> Any:
#     #     """
#     #     Creates a new session for the user and assigns the access token.
#     #     """
#     #     req_code = request.args.get('code')
#     #     self.token = self.auth_manager.get_access_token(req_code)
#     #     session[TOKEN_INFO] = self.token
#     #     token = check_token(session.get(TOKEN_INFO, None))
#     #     return token
#
#
# class SessionError(Exception):
#     """
#     Exception raised when session's token is None
#
#     Instance Attributes:
#         - message: message to be raised. Defaulted.
#     """
#
#     message: str
#
#     def __init__(self, msg="Error Occurred during the session's token extraction") -> None:
#         self.message = msg
#         super().__init__(self.message)
