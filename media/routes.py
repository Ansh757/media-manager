""" File For the Endpoints """

from media import app
from flask import render_template, redirect, url_for, session
from media.spotify_api import SessionError, check_token
from object.spotify_api import SpotifyAPI


# A Key within this a session


# Endpoint for Home Page
@app.route('/')
@app.route('/home')
def home_page():
    # TODO: Render home.html
    return render_template("home.html")


@app.route('/login')
def login_page():
    # sp_oauth = make_spotify_oauth(SECRET_CLIENT_ID, SECRET_KEY)
    # auth_url = sp_oauth.get_authorize_url()
    # return redirect(auth_url)
    sp_oauth = SpotifyAPI()
    sp_oauth.create_spotify_oauth("authorization_page", "user-library-read")
    auth_url = sp_oauth.auth_manager.get_authorize_url()
    return redirect(auth_url)


@app.route('/redirect')
def authorization_page():
    sp_oauth = SpotifyAPI()
    sp_oauth.create_spotify_oauth("authorization_page", "user-library-read")
    session.clear()
    sp_oauth.generate_new_session()
    # request_code = request.args.get('code')
    # session_token = sp_oauth.auth_manager.get_access_token(request_code)
    # session[SESSION_TOKEN] = session_token
    try:
        token_information = sp_oauth.check_token()
    except:
        raise SessionError
    return redirect(url_for("home_page", _external=True))


@app.route('/myTracks')
def tracks_page():
    

    return "List of my Tracks"
