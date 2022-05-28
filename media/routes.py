""" File For the Endpoints """
import sys

from media import app
from flask import render_template, redirect, url_for, session
from object.spotify_api import SpotifyAPI, SessionError


# A Key within this a session


# Endpoint for Home Page
@app.route('/')
@app.route('/home')
def home_page():
    # TODO: Render home.html
    return render_template("home.html")


@app.route('/login')
def login_page():
    sp_oauth = SpotifyAPI()
    sp_oauth.create_spotify_oauth("authorization_page", "user-library-read")
    auth_url = sp_oauth.auth_manager.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def authorization_page():
    sp_oauth = SpotifyAPI()
    sp_oauth.create_spotify_oauth("authorization_page", "user-library-read")
    session.clear()
    # sp_oauth.generate_new_session()

    # request_code = request.args.get('code')
    # session_token = sp_oauth.auth_manager.get_access_token(request_code)
    # session[SESSION_TOKEN] = session_token
    # TODO: BUG FOUND! Fix the refresh token and check token -- the extraction seem to have a bug
    try:
        token_information = sp_oauth.check_token()

    except:
        raise SessionError
    # return redirect("home")
    return "Authorize"


@app.route('/myTracks')
def tracks_page():
    

    return "List of my Tracks"
