"""
    Creating database to store all the extracted
    data from the Spotify API.
"""
from __future__ import annotations

from media import db, ma


# Class to store the Spotify Data
class SongData(db.Model):
    """
    ...
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
    ...
    """

    class Meta:
        """
        ...
        """
        fields = ('id', 'song_name', 'artist_name', 'song_uri',
                  'album_name', 'album_uri')


sp_data_schema = SongDataSchema()
sp_datas_schemas = SongDataSchema(many=True)
