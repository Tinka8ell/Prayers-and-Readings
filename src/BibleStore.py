# Bible Store contains all the active view of the Bible content

from pony.orm import *

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


class Verse(db.Entity):
    id = PrimaryKey(int, auto=True)
    Number = Required(int)
    Last = Optional(int)
    Content = Required(LongStr)
    chapter = Required('Chapter')
    lookups = Set('Lookup')


class Chapter(db.Entity):
    id = PrimaryKey(int, auto=True)
    Number = Required(int)
    Verses = Required(int)
    IsComplete = Required(bool, default=False)
    book = Required(Book)
    verses = Set(Verse)
    lookups = Set('Lookup')


class Lookup(db.Entity):
    id = PrimaryKey(int, auto=True)
    Number = Required(int)
    chapter = Required(Chapter)
    verse = Required(Verse)



ok = db.bind(provider='mysql', host='localhost', user='root', passwd='toor', db='bible_store')
ok = db.generate_mapping(create_tables=True)
