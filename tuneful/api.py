import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import decorators
from . import app
from .database import session, Song, File
from .utils import upload_path

@app.route("/api/songs")
@decorators.accept("application/json")
def get_songs():

    songs = session.query(Song)
    songs = songs.order_by(Song.file.name)
    data = json.dumps()
