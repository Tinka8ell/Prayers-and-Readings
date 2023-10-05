# Bible Store contains all the active view of the Bible content

from pony.orm import *
from os import environ as env
from dotenv import load_dotenv

load_dotenv()
db = Database()


class Version(db.Entity):
    id = PrimaryKey(int, auto=True)
    Abbreviation = Required(str, 0, unique=True)
    Name = Required(str)
    IsComplete = Optional(bool, default=False)
    Year = Required(int, default=0)
    Copyright = Optional(str)
    books = Set('Book')


class Book(db.Entity):
    id = PrimaryKey(int, auto=True)
    ExtendedAbbreviation = Required(str)
    Name = Required(str)
    Total = Required(int)
    IsComplete = Optional(bool, default=False)
    version = Required(Version)
    chapters = Set('Chapter')


class Chapter(db.Entity):
    id = PrimaryKey(int, auto=True)
    Number = Required(int)
    Verses = Required(int)
    IsComplete = Required(bool, default=False)
    book = Required(Book)
    verses = Set('Verse')
    lookups = Set('Lookup')


class Verse(db.Entity):
    id = PrimaryKey(int, auto=True)
    Number = Required(int)
    Last = Optional(int)
    Content = Required(LongStr)
    chapter = Required(Chapter)
    lookups = Set('Lookup')


class Lookup(db.Entity):
    id = PrimaryKey(int, auto=True)
    Number = Required(int)
    chapter = Required(Chapter)
    verse = Required(Verse)


_hostname = env.get('HOSTNAME')
if _hostname == None:
    raise Exception("[error]: 'HOSTNAME' environment variable required")
_user = env.get('HOSTUSER')
if _user == None:
    raise Exception("[error]: 'HOSTUSER' environment variable required")
_password = env.get('PASSWORD')
if _password == None:
    raise Exception("[error]: 'PASSWORD' environment variable required")
_database = env.get('DATABASE')
if _database == None:
    raise Exception("[error]: 'DATABASE' environment variable required")
db.bind(provider='mysql', host=_hostname, user=_user, passwd=_password, db=_database)
db.generate_mapping(create_tables=True)
