""" File For the Endpoints """
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from media import app

from flask import render_template, redirect, request, session, url_for
from credentials.credentials_info import SECRET_CLIENT_ID, SECRET_KEY, TOKEN_INFO
import time


# Endpoint for Home Page
@app.route('/')
@app.route('/home')
def home_page():
    # TODO: Render home.html
    return render_template("home.html")


@app.route('/login')
def login_page():
    sp_oauth = create_user_oauth()
    # # Gets the redirect url set up in the devs tools
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/redirect')
def authorization_page():
    sp_oauth = create_user_oauth()
    # Clear any previous sessions
    session.clear()
    # Request a new session access code token
    request_code = request.args.get('code')
    code = sp_oauth.get_access_token(request_code)
    session[TOKEN_INFO] = code
    return redirect(url_for('tracks_page', _external=True))


@app.route('/myTracks')
def tracks_page():
    global session_token
    try:
        # at this point, the access_token is valid
        session_token = check_token()
        # If Session Error is received, redirect back to the login
    except SessionError:
        redirect("/")

    sp = spotipy.Spotify(auth=session_token["access_token"])
    return sp.current_user_saved_tracks(20, 0)


def check_token() -> session:
    """
    Fetches the session's token then compares with token's expire time.
    If token is expired then generate a new one.
    """
    token = session.get(TOKEN_INFO, None)
    if not token:
        raise SessionError
    # Check if the token is expired
    current_time = int(time.time())
    expires = token["expires_at"] - current_time < 60
    if expires:
        # Create a new token
        sp_oauth = create_user_oauth()
        token = sp_oauth.refresh_access_token(token['refresh_token'])
    return token


def create_user_oauth() -> SpotifyOAuth:
    """
    Creates a SpotifyOAuth Object that sets the request ID and Key, then
    redirects user to authorization route.
    """
    sp = SpotifyOAuth(client_id=SECRET_CLIENT_ID, client_secret=SECRET_KEY,
                      redirect_uri=url_for("authorization_page", _external=True), scope="user-library-read")
    return sp


class SessionError(Exception):
    """
    Exception raised when session's token is None

    Instance Attributes:
        - message: message to be raised. Defaulted.
    """

    message: str

    def __init__(self, msg="Error Occurred during the session's token extraction") -> None:
        self.message = msg
        super().__init__(self.message)
