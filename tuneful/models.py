# The Song model: This should have an integer id column, and a column specifying a one-to-one relationship with a File.
# The File model: This should have an integer id column, a string column for the filename, and the backref from the one-to-one relationship with the Song.
from marshmallow import Schema, fields, pprint
from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

class Song(Base):
    __tablename__='songs'

    id = Column (Integer, primary_key=True)
    file = relationship ("File", uselist=False, backref='song')

    def as_dictionary(self):
        song = {
            'id': self.id,
            'file': self.file
        }
        return song

class File(Base):
    __tablename__='files'

    id = Column (Integer, primary_key=True)
    name = Column (String, nullable=False)
    song_id = Column (Integer, ForeignKey('songs.id'), nullable=False)

    def as_dictionary(self):
        file = {
            'id': self.id,
            'name': self.name,
            'song_id': self.song_id
        }
        return file

class FileSchema(Schema):
    id = fields.Integer()
    name = fields.String()


class SongSchema(Schema):
    id = fields.Integer()
    file = fields.Nested(FileSchema)
