""" File For the Endpoints """

from requests import session
from media import app
from media.credentials_info import SECRET_CLIENT_ID, SECRET_KEY
from flask import render_template, redirect, url_for, request, session
from spotipy.oauth2 import SpotifyOAuth


# A Key within this a session
SESSION_TOKEN = "session-token"

# Endpoint for Home Page
@app.route('/')
@app.route('/home')
def home_page():
    # TODO: Render home.html
    return render_template("home.html")


@app.route('/login')
def login_page():
    sp_oauth = make_spotify_oauth(SECRET_CLIENT_ID, SECRET_KEY)
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/redirect')
def authorization_page():
    sp_ouath = make_spotify_oauth(SECRET_CLIENT_ID, SECRET_KEY)
    session.clear()
    request_code = request.args.get('code')
    session_token = sp_ouath.get_access_token(request_code)
    session[SESSION_TOKEN] = session_token
    return redirect(url_for("home_page", _external=True))


@app.route('/myTracks')
def tracks_page():
    return "List of my Tracks"


def make_spotify_oauth(secret_client_id: str, secret_key: str):
    """
    Takes in Two parameters: secret_client, and secret_key that are associated with
    the app on the spotify developer build.
    """
    return SpotifyOAuth(client_id=secret_client_id,
                        client_secret=secret_key,
                        redirect_uri=url_for(
                            'authorization_page', _external=True),
                        scope="user-library-read")
