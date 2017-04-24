import unittest
import os
import shutil
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Py2 compatibility
from io import StringIO

# import sys; print(list(sys.modules.keys())) # IDEA: WHY DO I NEED THIS?
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session, Song, File, SongSchema, FileSchema

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



if __name__ == "__main__":
    unittest.main()
