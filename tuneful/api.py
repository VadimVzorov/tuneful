import json

from flask import request, Response, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import decorators
from . import app
from .database import session, Song, File, SongSchema, FileSchema
from .utils import upload_path

@app.route("/api/songs", methods = ['GET'])
@decorators.accept("application/json")
def get_songs():
    songs = session.query(Song)
    data = []
    for song in songs:
        results, errors = SongSchema().dump(song.as_dictionary())
        data.append(results)
    results = json.dumps(data)
    return Response(results, 200, mimetype="application/json")
