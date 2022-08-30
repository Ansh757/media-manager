""" File For the Endpoints """
import spotipy
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from media import app

from flask import render_template, redirect, request, session, url_for
from credentials.credentials_info import SECRET_CLIENT_ID, SECRET_KEY, TOKEN_INFO
import time
import datetime as dt
from media.models import SongData
from media import db
from typing import List

global user_ac_token


@app.route('/')
def default_page() -> object:
    """
    The Intro Page
    """
    return render_template("intro.html")


@app.route('/home', methods=['GET', 'POST'])
def home_page() -> object:
    """
    Home Page Route that renders the home.html
    """
    global session_token
    try:
        # at this point, the access_token is valid
        session_token = check_token()
        # If Session Error is received, redirect back to the login
    except SessionError:
        redirect("/")

    sp = spotipy.Spotify(auth=session_token["access_token"])

    artists_data = {}
    playlists_name = []

    # _token = request.args.get("messages")
    # sp = spotipy.Spotify(auth=_token)

    curr_song = sp.current_user_playing_track()
    top_five_artists_data = sp.current_user_top_artists(limit=5, offset=0, time_range="long_term")
    list_of_devices = sp.devices()
    list_of_playlists = traverse_playlists(sp)

    # If curr_song is there
    if curr_song:
        artist_name = str(curr_song['item']['artists'][0]['name'])
        song_image = str(curr_song["item"]["album"]["images"][0]["url"])
        song_name = str(curr_song["item"]["name"])
        options = "Currently Playing"
    else:
        curr_time = dt.datetime.combine(dt.datetime.now(), dt.time.min)
        unix_early_time = int(time.mktime(curr_time.timetuple()) * 1000)
        curr_song = sp.current_user_recently_played(limit=1, after=unix_early_time, before=None)

        artist_name = str(curr_song["items"][0]["track"]["album"]["artists"][0]["name"])
        song_image = str(curr_song["items"][0]["track"]["album"]["images"][0]["url"])
        song_name = str(curr_song["items"][0]["track"]["name"])
        options = "Last Played"

    # Get the Top Artists
    for i in range(5):
        lst = [top_five_artists_data["items"][i]["name"], top_five_artists_data["items"][i]["images"][0]["url"]]
        artists_data[i] = lst

    # if Length of Playlist is Even
    if len(list_of_playlists) % 2 == 0:
        for i in range(0, len(list_of_playlists), 2):
            lst = [list_of_playlists[i]["name"], list_of_playlists[i + 1]["name"]]
            playlists_name.append(lst)
    else:
        for i in range(0, len(list_of_playlists), 2):
            if i == len(list_of_playlists) - 1:
                playlists_name.append(playlists_name.append(list_of_playlists[i]["name"]))
            else:
                lst = [list_of_playlists[i]["name"], list_of_playlists[i + 1]["name"]]
                playlists_name.append(lst)

    # Combine everything into a dictionary
    curr_song_data = {
        "artist_name": artist_name,
        "image": song_image,
        "song_name": song_name,
        "option": options,
        "top_artists": artists_data,
        "devices": list_of_devices,
        "playlist": playlists_name
    }

    return render_template("home.html", items=curr_song_data)


@app.route('/login')
def login_page() -> object:
    """
    A step before the login page -- gets the redirect url that
    redirects the user to the Spotify OAuthorization page
    """
    sp_oauth = create_user_oauth()
    # Gets the redirect url set up in the devs tools
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
    return redirect(url_for('home_page', _external=True))


@app.route('/myTracks', methods=['GET', 'POST'])
def tracks_page() -> object:
    """
        Saved Tracks Page
    """
    global session_token
    try:
        # at this point, the access_token is valid
        session_token = check_token()
        # If Session Error is received, redirect back to the login
    except SessionError:
        redirect("/")

    sp = spotipy.Spotify(auth=session_token["access_token"])

    raw_list_of_songs = traverse(sp)

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

    all_songs = SongData.query.all()
    return render_template("tracks.html", items=all_songs)

#
# @app.route('/myArtists', methods=['GET', 'POST'])
# def tracks_page() -> object:
#     """
#         Saved Tracks Page
#     """
#     global session_token
#     try:
#         # at this point, the access_token is valid
#         session_token = check_token()
#         # If Session Error is received, redirect back to the login
#     except SessionError:
#         redirect("/")
#
#     sp = spotipy.Spotify(auth=session_token["access_token"])
#
#     raw_list_of_artists = traverse_artists(sp)
#
#     for i in range(len(raw_list_of_artists)):
#
#         # Create a SD Object for each song
#         artist_name = str(raw_list_of_artists[i]['track']['artists'][0]['name'])
#         song_name = str(raw_list_of_artists[i]['track']['name'])
#         song_uri = str(raw_list_of_artists[i]['track']['artists'][0]['uri'])
#         album_name = str(raw_list_of_artists[i]['track']['album']['name'])
#         album_uri = str(raw_list_of_artists[i]['track']['album']['uri'])
#         sd = ArtistData(song_name, artist_name, album_uri, album_name, song_uri)
#
#         # Add to the current session
#         db.session.add(sd)
#
#         if db.session.query(ArtistData).count() % 50 == 0:
#             db.session.commit()
#
#     db.session.commit()
#
#     all_songs = ArtistDate.query.all()
#     return render_template("tracks.html", items=all_songs)
#     # flash('Successful! Your data has been loaded!', category='success')
#

@app.route('/logout')
def logout_page() -> object:
    """
    Logouts the current sessions
    """
    session.clear()
    return redirect('/')


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
def create_tables() -> None:
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
                      redirect_uri=url_for("authorization_page", _external=True),
                      scope="user-library-read user-read-currently-playing user-read-recently-played user-top-read "
                            "user-read-playback-state playlist-read-private")
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


def traverse(sp: Spotify) -> List:
    """
    Helper for traversing through the saved tracks .
    """
    lst = []
    counter = 0
    while True:
        items = sp.current_user_saved_tracks(limit=50, offset=counter * 50)["items"]

        counter += 1
        lst += items
        if len(items) < 50:
            break
    return lst


def traverse_artists(sp: Spotify) -> List:
    """
    Helper for traversing through the saved tracks .
    """
    lst = []
    counter = 0
    while True:
        items = sp.current_user_saved_tracks(limit=50, offset=counter * 50)["items"]

        counter += 1
        lst += items
        if len(items) < 50:
            break
    return lst

def traverse_playlists(sp: Spotify) -> List:
    """
    Helper for traversing through the playlists.
    """
    lst = []
    counter = 0
    while True:
        items = sp.current_user_playlists(limit=50, offset=counter * 50)["items"]
        counter += 1
        lst += items
        if len(items) < 50:
            break
    return lst
