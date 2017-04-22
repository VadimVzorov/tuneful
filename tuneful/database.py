from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from . import app

engine = create_engine(app.config["DATABASE_URI"])
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()



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

Base.metadata.create_all(engine)
