import json
from jsonschema import validate, ValidationError

from flask import render_template, request, Response, url_for

from tuneful import app
from .database import session, Song, File


@app.route("/")
def index():
    import pdb; pdb.set_trace()
    return app.send_static_file("index.html")
