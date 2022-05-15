""" File For the Endpoints """

from media import app
from media.credentials_info import SECRET_CLIENT_ID, SECRET_KEY
from flask import render_template, redirect, url_for, request
from media.login_auth import make_spotify_oauth


# Endpoint for Home Page
@app.route('/')
@app.route('/home')
def home_page():
    # TODO: Render home.html
    return "Ansh Home"


@app.route('/login')
def login_page():
    sp_oauth = make_spotify_oauth(SECRET_CLIENT_ID, SECRET_KEY)
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/redirect')
def authorization_page():
    return "authorization"


@app.route('/myTracks')
def tracks_page():
    return "List of my Tracks"



