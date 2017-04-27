import json

from flask import request, Response, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError
from io import BytesIO, StringIO

from . import decorators
from . import app
from .database import session
from .utils import upload_path
from .models import Song, File, SongSchema, FileSchema

@app.route("/api/songs", methods = ['GET'])
@decorators.accept("application/json")
def get_songs():
    songs = session.query(Song).join(Song.file).order_by(File.name)
    data = []
    for song in songs:
        result, errors = SongSchema().dump(song.as_dictionary())
        data.append(result)
    results = json.dumps(data)
    return Response(results, 200, mimetype="application/json")

@app.route("/api/songs/<string:name>", methods=["GET"])
@decorators.accept("application/json")
def get_song(name):
    song = session.query(Song).join(Song.file).filter(File.name == name).first()
    result, errors = SongSchema().dump(song.as_dictionary())
    data = json.dumps(result)
    return Response(data, 200, mimetype="application/json")

@app.route("/api/songs", methods = ['POST'])
@decorators.accept("application/json")
@decorators.require("application/json")
def post_songs():
    data = request.json
    import pdb; pdb.set_trace()
    name = data['file']['name']
    song = Song()
    file = File(name = name, song = song)
    session.add_all([song, file])
    session.commit()
    result, errors = SongSchema().dump(song.as_dictionary())
    data = json.dumps(result)
    headers = {"Location": url_for("get_song", name = name)}
    return Response(data, 201, headers=headers, mimetype="application/json")

@app.route("/api/songs", methods = ['PUT'])
@decorators.accept("application/json")
@decorators.require("application/json")
def put_songs():
    data = request.json
    name = data['file']['name']
    new_name = data['file']['new_name']
    song = session.query(Song).join(Song.file).filter(File.name == name).first()
    song.file.name = new_name
    session.commit()
    result, errors = SongSchema().dump(song.as_dictionary())
    data = json.dumps(result)
    headers = {"Location": url_for("get_song", name = name)}
    return Response(data, 201, headers=headers, mimetype="application/json")

@app.route("/api/song/<string:name>/delete", methods = ['DELETE'])
@decorators.accept("application/json")
def delete_song(name):
    song = session.query(Song).join(Song.file).filter(File.name == name).first()
    file = session.query(File).filter(File.name == name).first()
    session.delete(song)
    session.delete(file)
    session.commit()
    message = "Deleted song {}".format(name)
    data = json.dumps({"message":message})
    return Response (data, 200, mimetype="application/json")

@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(upload_path(), filename)

@app.route("/api/files", methods=["POST"])
@decorators.require("multipart/form-data")
@decorators.accept("application/json")
def file_post():
    file = request.files.get("file")
    if not file:
        data = {"message": "Could not find file data"}
        return Response(json.dumps(data), 422, mimetype="application/json")

    filename = secure_filename(file.filename)
    song = Song()
    db_file = File(name=filename, song = song)
    session.add_all([song,db_file])
    session.commit()
    file.save(upload_path(filename))

    data = db_file.as_dictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")
