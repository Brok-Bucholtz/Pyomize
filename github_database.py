from sqlalchemy import Column, ForeignKey, Integer, String, UnicodeText, Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from ConfigParser import ConfigParser

Base = declarative_base()
config = ConfigParser()
config.read('config.ini')


class File(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    filename = Column(Unicode(260))
    sha = Column(Unicode(40))
    additions = Column(Integer)
    deletions = Column(Integer)
    changes = Column(Integer)
    status = Column(Unicode(256))
    patch = Column(UnicodeText)
    commit_id = Column(Integer, ForeignKey('commit.id'))


class Commit(Base):
    __tablename__ = 'commit'
    id = Column(Integer, primary_key=True)
    sha = Column(Unicode(40))
    date = Column(String(256))
    message = Column(UnicodeText)
    committer_email = Column(Unicode(256))
    organization_login = Column(Unicode(256))
    repository_name = Column(Unicode(256))
    files = relationship(File)

engine = create_engine(config.get('Main', 'LocalGithubDB'))
Base.metadata.create_all(engine)
