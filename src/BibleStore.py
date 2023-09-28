# Bible Store contains all the active view of the Bible content
"""
    CREATE TABLE `version` (
      `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
      `abbreviation` LONGTEXT UNIQUE NOT NULL,
      `name` VARCHAR(255) NOT NULL,
      `iscomplete` BOOLEAN NOT NULL,
      `year` INTEGER NOT NULL,
      `copyright` VARCHAR(255) NOT NULL
    );

    CREATE TABLE `book` (
      `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
      `extenedabbreviation` VARCHAR(255) NOT NULL,
      `name` VARCHAR(255) NOT NULL,
      `total` INTEGER NOT NULL,
      `iscomplete` BOOLEAN NOT NULL,
      `version` INTEGER NOT NULL
    );

    CREATE INDEX `idx_book__version` ON `book` (`version`);

    ALTER TABLE `book` ADD CONSTRAINT `fk_book__version` FOREIGN KEY (`version`) REFERENCES `version` (`id`) ON DELETE CASCADE;

    CREATE TABLE `chapter` (
      `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
      `number` INTEGER NOT NULL,
      `verses` INTEGER NOT NULL,
      `iscomplete` BOOLEAN NOT NULL,
      `book` INTEGER NOT NULL
    );

    CREATE INDEX `idx_chapter__book` ON `chapter` (`book`);

    ALTER TABLE `chapter` ADD CONSTRAINT `fk_chapter__book` FOREIGN KEY (`book`) REFERENCES `book` (`id`) ON DELETE CASCADE;

    CREATE TABLE `verse` (
      `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
      `number` INTEGER NOT NULL,
      `last` INTEGER,
      `content` LONGTEXT NOT NULL,
      `chapter` INTEGER NOT NULL
    );

    CREATE INDEX `idx_verse__chapter` ON `verse` (`chapter`);

    ALTER TABLE `verse` ADD CONSTRAINT `fk_verse__chapter` FOREIGN KEY (`chapter`) REFERENCES `chapter` (`id`) ON DELETE CASCADE;

    CREATE TABLE `lookup` (
      `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
      `number` INTEGER NOT NULL,
      `chapter` INTEGER NOT NULL,
      `verse` INTEGER NOT NULL
    );

    CREATE INDEX `idx_lookup__chapter` ON `lookup` (`chapter`);

    CREATE INDEX `idx_lookup__verse` ON `lookup` (`verse`);

    ALTER TABLE `lookup` ADD CONSTRAINT `fk_lookup__chapter` FOREIGN KEY (`chapter`) REFERENCES `chapter` (`id`) ON DELETE CASCADE;

    ALTER TABLE `lookup` ADD CONSTRAINT `fk_lookup__verse` FOREIGN KEY (`verse`) REFERENCES `verse` (`id`) ON DELETE CASCADE
"""

from pony.orm import *


db = Database()


class Version(db.Entity):
    id = PrimaryKey(int, auto=True)
    Abbreviation = Required(str, 0, unique=True)
    Name = Required(str)
    IsComplete = Required(bool, default=False)
    Year = Required(int, default=0)
    Copyright = Optional(str)
    books = Set('Book')


class Book(db.Entity):
    id = PrimaryKey(int, auto=True)
    ExtenedAbbreviation = Required(str)
    Name = Required(str)
    Total = Required(int)
    IsComplete = Required(bool, default=False)
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



db.bind(provider='mysql', host='localhost', user='root', passwd='toor', db='bible_store')
db.generate_mapping(create_tables=True)
