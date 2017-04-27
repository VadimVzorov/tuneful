import unittest
import os
import shutil
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Py2 compatibility
from io import StringIO, BytesIO


# import sys; print(list(sys.modules.keys())) # IDEA: WHY DO I NEED THIS?
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session
from tuneful.models import Song, File, SongSchema, FileSchema

class TestAPI(unittest.TestCase):
    """ Tests for the tuneful API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())

    def create_songs(self):
        songB = Song()
        fileB = File(name = 'SongB', song = songB)
        songA = Song()
        fileA = File(name = 'SongA', song = songA)
        session.add_all([songA, songB])
        session.commit()

    def test_get_empty(self):
        response = self.client.get('api/songs',
            headers = [('Accept', 'application/json')])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/json')
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual (data, [])

    def test_get_songs(self):
        self.create_songs()
        response = self.client.get('api/songs',
            headers = [('Accept', 'application/json')])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/json')
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['file']['name'], 'SongA')
        self.assertEqual(data[1]['file']['name'], 'SongB')

    def test_get_song(self):
        self.create_songs()
        response = self.client.get('api/songs/SongA',
            headers = [('Accept', 'application/json')]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/json')
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(data['file']['name'], 'SongA')

    def test_add_song(self):
        data = {
            "file":{
                "name": "test"
            }
        }
        response = self.client.post("api/songs",
            data = json.dumps(data),
            content_type = "application/json",
            headers = [("Accept", "application/json")]
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, 'application/json')
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(data['file']['name'], 'test')

    def test_change_song_name(self):
        self.create_songs()
        data = {
            "file":{
                "name":"SongA",
                "new_name":"SongC"
            }
        }
        response = self.client.put("api/songs",
            data = json.dumps(data),
            content_type = "application/json",
            headers = [("Accept", "application/json")]
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, 'application/json')
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(data['file']['name'], 'SongC')

    def test_delete_song(self):
        self.create_songs()
        songA = session.query(Song).join(Song.file).filter(File.name == 'SongA').first()
        response = self.client.delete("api/song/SongA/delete",
            headers = [("Accept", "application/json")]
        )
        songs = session.query(Song).all()
        self.assertNotIn(songA, songs)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data['message'], "Deleted song SongA")

    def test_get_uploaded_file(self):
        path =  upload_path("test.txt")
        with open(path, "wb") as f:
            f.write(b"File contents")

        response = self.client.get("/uploads/test.txt")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/plain")
        self.assertEqual(response.data, b"File contents")

    def test_file_upload(self):
        data = {
            "file": (BytesIO(b"File contents"), "test.txt")
        }

        response = self.client.post("/api/files",
            data=data,
            content_type="multipart/form-data",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(urlparse(data["path"]).path, "/uploads/test.txt")

        path = upload_path("test.txt")
        self.assertTrue(os.path.isfile(path))
        with open(path, "rb") as f:
            contents = f.read()
        self.assertEqual(contents, b"File contents")

if __name__ == "__main__":
    unittest.main()
