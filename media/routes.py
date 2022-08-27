""" File For the Endpoints """
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from media import app

from flask import render_template, redirect, request, session, url_for, flash
from credentials.credentials_info import SECRET_CLIENT_ID, SECRET_KEY, TOKEN_INFO
import time
import datetime as dt
from media.models import SongData
from media import db

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
    _token = request.args.get("messages")
    sp = spotipy.Spotify(auth=_token)

    curr_song = sp.current_user_playing_track()
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


    # Combine everything into a dictionary
    curr_song_data = {
        "artist_name": artist_name,
        "image": song_image,
        "song_name": song_name,
        "option": options
    }


    # all_songs = SongData.query.all()
    # return render_template("home.html", songs=curr_song, items=all_songs)
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

    user_ac_token = session_token["access_token"]

    sp = spotipy.Spotify(auth=session_token["access_token"])
    # raw_list_of_songs = sp.current_user_playing_track()

    raw_list_of_songs = []
    counter = 0
    while True:
        # curr_time = dt.datetime.combine(dt.datetime.now(), dt.time.min)
        # unix_early_time = int(time.mktime(curr_time.timetuple()) * 1000)
        # items = sp.current_user_recently_played(limit=2, after=unix_early_time, before=None)

        items = sp.current_user_saved_tracks(limit=50, offset=counter * 50)["items"]
        # sp.current_user_top_tracks(20, 0)["items"]
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
    # return str(raw_list_of_songs)
    return redirect(url_for('home_page', messages=user_ac_token, _external=True))

    # flash('Successful! Your data has been loaded!', category='success')


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
                      scope="user-library-read user-read-recently-played user-top-read")
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

# #
# {'timestamp': 1661447732479,
#  'context': {'external_urls': {'spotify': 'https://open.spotify.com/album/47Thm1tltjJVofuRumhfmi'},
#              'href': 'https://api.spotify.com/v1/albums/47Thm1tltjJVofuRumhfmi', 'type': 'album',
#              'uri': 'spotify:album:47Thm1tltjJVofuRumhfmi'}, 'progress_ms': 55188, 'item': {
#     'album': {'album_type': 'album', 'artists': [
#         {'external_urls': {'spotify': 'https://open.spotify.com/artist/0Njy6yR9LykNKYg9yE23QN'},
#          'href': 'https://api.spotify.com/v1/artists/0Njy6yR9LykNKYg9yE23QN', 'id': '0Njy6yR9LykNKYg9yE23QN',
#          'name': 'Nardo Wick', 'type': 'artist', 'uri': 'spotify:artist:0Njy6yR9LykNKYg9yE23QN'}],
#               'available_markets': ['AD', 'AE', 'AG', 'AL', 'AM', 'AO', 'AR', 'AT', 'AU', 'AZ', 'BA', 'BB', 'BD', 'BE',
#                                     'BF', 'BG', 'BH', 'BI', 'BJ', 'BN', 'BO', 'BR', 'BS', 'BT', 'BW', 'BY', 'BZ', 'CA',
#                                     'CD', 'CG', 'CH', 'CI', 'CL', 'CM', 'CO', 'CR', 'CV', 'CW', 'CY', 'CZ', 'DE', 'DJ',
#                                     'DK', 'DM', 'DO', 'DZ', 'EC', 'EE', 'EG', 'ES', 'FI', 'FJ', 'FM', 'FR', 'GA', 'GB',
#                                     'GD', 'GE', 'GH', 'GM', 'GN', 'GQ', 'GR', 'GT', 'GW', 'GY', 'HK', 'HN', 'HR', 'HT',
#                                     'HU', 'ID', 'IE', 'IL', 'IN', 'IQ', 'IS', 'IT', 'JM', 'JO', 'JP', 'KE', 'KG', 'KH',
#                                     'KI', 'KM', 'KN', 'KR', 'KW', 'KZ', 'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS', 'LT',
#                                     'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MG', 'MH', 'MK', 'ML', 'MN', 'MO', 'MR',
#                                     'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ', 'NA', 'NE', 'NG', 'NI', 'NL', 'NO', 'NP',
#                                     'NR', 'NZ', 'OM', 'PA', 'PE', 'PG', 'PH', 'PK', 'PL', 'PS', 'PT', 'PW', 'PY', 'QA',
#                                     'RO', 'RS', 'RW', 'SA', 'SB', 'SC', 'SE', 'SG', 'SI', 'SK', 'SL', 'SM', 'SN', 'SR',
#                                     'ST', 'SV', 'SZ', 'TD', 'TG', 'TH', 'TJ', 'TL', 'TN', 'TO', 'TR', 'TT', 'TV', 'TW',
#                                     'TZ', 'UA', 'UG', 'US', 'UY', 'UZ', 'VC', 'VE', 'VN', 'VU', 'WS', 'XK', 'ZA', 'ZM',
#                                     'ZW'],
#               'external_urls': {'spotify': 'https://open.spotify.com/album/47Thm1tltjJVofuRumhfmi'},
#               'href': 'https://api.spotify.com/v1/albums/47Thm1tltjJVofuRumhfmi', 'id': '47Thm1tltjJVofuRumhfmi',
#               'images': [{'height': 640, 'url': 'https://i.scdn.co/image/ab67616d0000b273b61d76c602c6234f937446c4',
#                           'width': 640},
#                          {'height': 300, 'url': 'https://i.scdn.co/image/ab67616d00001e02b61d76c602c6234f937446c4',
#                           'width': 300},
#                          {'height': 64, 'url': 'https://i.scdn.co/image/ab67616d00004851b61d76c602c6234f937446c4',
#                           'width': 64}], 'name': 'Who is Nardo Wick?? (Deluxe)', 'release_date': '2022-07-22',
#               'release_date_precision': 'day', 'total_tracks': 30, 'type': 'album',
#               'uri': 'spotify:album:47Thm1tltjJVofuRumhfmi'}, 'artists': [
#         {'external_urls': {'spotify': 'https://open.spotify.com/artist/0Njy6yR9LykNKYg9yE23QN'},
#          'href': 'https://api.spotify.com/v1/artists/0Njy6yR9LykNKYg9yE23QN', 'id': '0Njy6yR9LykNKYg9yE23QN',
#          'name': 'Nardo Wick', 'type': 'artist', 'uri': 'spotify:artist:0Njy6yR9LykNKYg9yE23QN'}],
#     'available_markets': ['AD', 'AE', 'AG', 'AL', 'AM', 'AO', 'AR', 'AT', 'AU', 'AZ', 'BA', 'BB', 'BD', 'BE', 'BF',
#                           'BG', 'BH', 'BI', 'BJ', 'BN', 'BO', 'BR', 'BS', 'BT', 'BW', 'BY', 'BZ', 'CA', 'CD', 'CG',
#                           'CH', 'CI', 'CL', 'CM', 'CO', 'CR', 'CV', 'CW', 'CY', 'CZ', 'DE', 'DJ', 'DK', 'DM', 'DO',
#                           'DZ', 'EC', 'EE', 'EG', 'ES', 'FI', 'FJ', 'FM', 'FR', 'GA', 'GB', 'GD', 'GE', 'GH', 'GM',
#                           'GN', 'GQ', 'GR', 'GT', 'GW', 'GY', 'HK', 'HN', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IN',
#                           'IQ', 'IS', 'IT', 'JM', 'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KR', 'KW', 'KZ',
#                           'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME',
#                           'MG', 'MH', 'MK', 'ML', 'MN', 'MO', 'MR', 'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ', 'NA',
#                           'NE', 'NG', 'NI', 'NL', 'NO', 'NP', 'NR', 'NZ', 'OM', 'PA', 'PE', 'PG', 'PH', 'PK', 'PL',
#                           'PS', 'PT', 'PW', 'PY', 'QA', 'RO', 'RS', 'RW', 'SA', 'SB', 'SC', 'SE', 'SG', 'SI', 'SK',
#                           'SL', 'SM', 'SN', 'SR', 'ST', 'SV', 'SZ', 'TD', 'TG', 'TH', 'TJ', 'TL', 'TN', 'TO', 'TR',
#                           'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'US', 'UY', 'UZ', 'VC', 'VE', 'VN', 'VU', 'WS', 'XK',
#                           'ZA', 'ZM', 'ZW'], 'disc_number': 2, 'duration_ms': 150798, 'explicit': True,
#     'external_ids': {'isrc': 'USRC12103535'},
#     'external_urls': {'spotify': 'https://open.spotify.com/track/0ThckDUL3cPr5OyoMlCnoD'},
#     'href': 'https://api.spotify.com/v1/tracks/0ThckDUL3cPr5OyoMlCnoD', 'id': '0ThckDUL3cPr5OyoMlCnoD',
#     'is_local': False, 'name': 'Bad Boy', 'popularity': 44,
#     'preview_url': 'https://p.scdn.co/mp3-preview/090e83be9c4e21a88576459b3bfc61b1c0956ce1?cid=4934417ccd344dd1877f05ed4a5d243a',
#     'track_number': 16, 'type': 'track', 'uri': 'spotify:track:0ThckDUL3cPr5OyoMlCnoD'},
#  'currently_playing_type': 'track', 'actions': {'disallows': {'resuming': True}}, 'is_playing': True}
