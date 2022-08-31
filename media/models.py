"""
    Creating database to store all the extracted
    data from the Spotify API.
"""
from __future__ import annotations

from media import db, ma


# Class to store the Spotify Data
class SongData(db.Model):
    """
    Song Data class to store the information of each song.
    """
    id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(length=50), unique=False, nullable=False)
    artist_name = db.Column(db.String(length=100), nullable=False)
    album_uri = db.Column(db.String(length=100), unique=False, nullable=False)
    album_name = db.Column(db.String(length=100), unique=False, nullable=True)
    song_uri = db.Column(db.String(length=100), unique=False, nullable=False)

    def __init__(self,
                 song_name: str,
                 artist_name: str,
                 album_uri: str,
                 album_name: str,
                 song_uri: str) -> None:
        self.song_name = song_name
        self.artist_name = artist_name
        self.song_uri = song_uri
        self.album_name = album_name
        self.album_uri = album_uri


class SongDataSchema(ma.Schema):
    """
    SongData Schema to store the fields.
    """

    class Meta:
        """
        Fields in the Database
        """
        fields = ('id', 'song_name', 'artist_name', 'song_uri',
                  'album_name', 'album_uri')


sp_data_schema = SongDataSchema()
sp_datas_schemas = SongDataSchema(many=True)


# Class to store the Artists Data
class ArtistData(db.Model):
    """
    Artist Data Class to store the names of Artists.
    """
    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(length=100), nullable=False)
    image_url = db.Column(db.String(length=100), nullable=False)

    def __init__(self,
                 artist_name: str,
                 image_url: str) -> None:
        self.artist_name = artist_name
        self.image_url = image_url


class ArtistDataSchema(ma.Schema):
    """
    ArtistData Schema to define the fields.
    """

    class Meta:
        """
        Fields in the database.
        """
        fields = ('id', 'artist_name', 'image_url')


artist_data_schema = ArtistDataSchema()
artist_datas_schemas = ArtistDataSchema(many=True)
