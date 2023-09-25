# Bible Store contains all the active view of the Bible content

from pony.orm import *


db = Database()


class Version(db.Entity):
    id = PrimaryKey(int, auto=True)
    Abbreviation = Required(str, 0, unique=True)
    Name = Required(str)
    books = Set('Book')


class Book(db.Entity):
    id = PrimaryKey(int, auto=True)
    ExtenedAbbreviation = Required(str)
    Name = Required(str)
    Total = Required(int)
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
    verses = Set(Verse)
    lookups = Set('Lookup')
    book = Required(Book)


class Lookup(db.Entity):
    id = PrimaryKey(int, auto=True)
    Number = Required(int)
    chapter = Required(Chapter)
    verse = Required(Verse)


db.bind(provider='mysql', host='localhost', user='root', passwd='toor', db='bible_store')
db.generate_mapping(create_tables=True)


"""
# Module Imports
import mariadb
import sys

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="root",
        password="toor",
        host="localhost",
        port=3306,
        database="biblestore"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()
"""
"""
* Bibles with contain:
  * Versions:
    * Id
    * Abrieviation (key)
    * Name
    * Later these will need:
      * Completed flag
      * Copyright details including:
        * Timestamp to identify updated content
  * Books
    * Id
    * Extended abrieviation (key)
    * Name
    * NumberOfChapters (last chapter number)
    * Version.Id (foreign key)
    * And later the other stuff
  * Chapters
    * Id
    * Number (key)
    * NumberOfVerses (last verse number)
    * Book.Id (foreign key)
    * Version.Id - maybe (foreign key)
  * Verses
    * Id
    * Number (some versions have number range) (key)
    * Content (could be template or html format?)
    * Chapter.Id (foreign key)
    * Book.Id - maybe (foreign key)
    * Version.Id - maybe (foreign key)
  * VerseLookUps
    * Id
    * Number (for each number in 1..Chapter.NumberOfVerses) (key)
    * Verse.Id (usually 1 - 1 mapping, but could be many - 1 mapping)
    * Chapter.Id (foreign key)
    * Book.Id - maybe (foreign key)
    * Version.Id - maybe (foreign key)
"""

