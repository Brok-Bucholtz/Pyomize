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
    commit = relationship('Commit', back_populates='files')


class Commit(Base):
    __tablename__ = 'commit'
    id = Column(Integer, primary_key=True)
    sha = Column(Unicode(40))
    date = Column(String(256))
    message = Column(UnicodeText)
    committer_email = Column(Unicode(256))
    files = relationship(File)

    repository_id = Column(Integer, ForeignKey('repository.id'))
    repository = relationship('Repository', back_populates='commits')


class Repository(Base):
    __tablename__ = 'repository'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(256))
    owner_login = Column(Unicode(256))

    commits = relationship('Commit', back_populates='repository')

engine = create_engine(config.get('Main', 'LocalGithubDB'))
Base.metadata.create_all(engine)
