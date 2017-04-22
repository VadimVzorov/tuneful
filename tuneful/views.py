import json
from jsonschema import validate, ValidationError

from flask import render_template, request, Response, url_for

from tuneful import app
from .database import session, Song, File, SongSchema, FileSchema

class ComplexEncoder(json.JSONEncoder):
     def default(self, obj):
         if isinstance(obj, complex):
             return [obj.real, obj.imag]
        # Let the base class default method raise the TypeError
         return json.JSONEncoder.default(self, obj)


@app.route("/")
def index():
    import pdb; pdb.set_trace()
    return app.send_static_file("index.html")
