""" File For the Endpoints """
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from media import app

from flask import render_template, redirect, request, session, url_for, flash
from credentials.credentials_info import SECRET_CLIENT_ID, SECRET_KEY, TOKEN_INFO
import time

from media.models import SongData
from media import db


# Endpoint for Home Page
@app.route('/')
def default_page() -> object:
    """
    The Login Page
    """
    return render_template("intro.html")


@app.route('/home', methods=['GET', 'POST'])
def home_page() -> object:
    """
    Home Page Route that renders the home.html
    """
    all_songs = SongData.query.all()
    return render_template("home.html", items=all_songs)


@app.route('/login')
def login_page() -> object:
    """
    A step before the login page -- gets the redirect url that
    redirects the user to the Spotify OAuthorization page
    """
    sp_oauth = create_user_oauth()
    # # Gets the redirect url set up in the devs tools
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/redirect')
def authorization_page() -> object:
    """
    This route comes from the redirected url and upon login, brings the users tracks.
    """
    sp_oauth = create_user_oauth()
    # Clear any previous sessions
    session.clear()
    # Request a new session access code token
    request_code = request.args.get('code')
    code = sp_oauth.get_access_token(request_code)
    session[TOKEN_INFO] = code
    return redirect(url_for('tracks_page', _external=True))


@app.route('/myTracks', methods=['GET'])
def tracks_page():
    global session_token
    try:
        # at this point, the access_token is valid
        session_token = check_token()
        # If Session Error is received, redirect back to the login
    except SessionError:
        redirect("/")

    sp = spotipy.Spotify(auth=session_token["access_token"])
    raw_list_of_songs = []
    counter = 0
    while True:

        items = sp.current_user_saved_tracks(limit=50, offset=counter * 50)["items"]
        #     sp.current_user_top_tracks(20, 0)["items"]
        counter += 1
        raw_list_of_songs += items
        if len(items) < 50:
            break

    # return str(sp.current_user_saved_tracks(20, 0)["items"][0]['track']['artists'][0]['name'])
    # return str(raw_list_of_songs)

    for i in range(len(raw_list_of_songs)):

        # Create a SD Object for each song
        artist_name = str(raw_list_of_songs[i]['track']['artists'][0]['name'])
        song_name = str(raw_list_of_songs[i]['track']['name'])
        song_uri = str(raw_list_of_songs[i]['track']['artists'][0]['uri'])
        album_name = str(raw_list_of_songs[i]['track']['album']['name'])
        album_uri = str(raw_list_of_songs[i]['track']['album']['uri'])
        sd = SongData(song_name, artist_name, album_uri, album_name, song_uri)

        # Add to the current session
        db.session.add(sd)

        if db.session.query(SongData).count() % 50 == 0:
            db.session.commit()

    db.session.commit()
    # return raw_list_of_songs
    return redirect(url_for('home_page', _external=True))

    # flash('Successful! Your data has been loaded!', category='success')


# @app.route('/songs', methods=['GET', 'POST'])
# def songs_page():
#     all_songs = SongData.query.all()
#     # result = sp_datas_schemas.dump(all_songs)
#     # data_in_json = flask.jsonify(result.data)
#     return render_template("tracks.html", items=all_songs)


@app.route('/logout')
def logout_page() -> object:
    """
    Logouts the current sessions
    """
    session.clear()
    return render_template('home.html')


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


@app.before_first_request
def create_tables():
    """
    Before the first request do the following: reset any databases, and then re-initialize.
    """
    db.drop_all()
    db.create_all()


def create_user_oauth() -> SpotifyOAuth:
    """
    Creates a SpotifyOAuth Object that sets the request ID and Key, then
    redirects user to authorization route.
    """
    sp = SpotifyOAuth(client_id=SECRET_CLIENT_ID, client_secret=SECRET_KEY,
                      redirect_uri=url_for("authorization_page", _external=True), scope="user-read-private "
                                                                                        "user-read-email "
                                                                                        "user-read-playback-state "
                                                                                        "user-modify-playback-state")
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
