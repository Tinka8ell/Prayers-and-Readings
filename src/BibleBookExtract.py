# Process a book of a bible version
#
#     Requires: 
#         Version abrieviation
#         Book abrieviation (can be full name)
#             Optional book number and space
#             At least fist 3 characters of name
#
#     Look up a bible reference on Bible Gateway.
#
#     Default to anglicised NIV(UK), but can be overridden with version.
#     Using WebTree read the page and extract the content as marked up text.
#     So skip titles, headings and chapter numbers.
#     Also skip footnotes and references.
#     Try to add as much relevant formatting and verse markers.
#     Add all verses (if not already in the Bible Store)
#     Identify the next and previous chapters that need to be processed

from BibleStore import *
from BibleChapterExtract import BibleChapterExtract
from time import sleep

class BibleBookExtract():
    """
    Process a book of a bible version

        Requires: 
            Version abrieviation
            Book abrieviation (can be full name)
                Optional book number and space
                At least fist 3 characters of name
        Look up a bible reference on Bible Gateway.

        Default to anglicised NIV(UK), but can be overridden with version.
        Using WebTree read the page and extract the content as marked up text.
        So skip titles, headings and chapter numbers.
        Also skip footnotes and references.
        Try to add as much relevant formatting and verse markers.
        Add all verses (if not already in the Bible Store)
        Identify the next and previous chapters that need to be processed
    """

    def __init__(self, book, version="NIVUK", delay=1, isDebug=False):  # default to English NIV
        self.isDebug = isDebug
        self.nextBook = None
        self.prevBook = None
        chapter = BibleChapterExtract(book, 1, version=version, isDebug=self.isDebug)
        self.Book = chapter.bibleStoreBook
        if chapter.prevChapter != None:
            self.prevBook = chapter.prevChapter.Book.Name
        if self.isDebug:
            if chapter.nextChapter != None:
                print("This book:", self.Book.ExtendedAbbreviation, "next book:", chapter.nextChapter.Book.ExtendedAbbreviation)
            else:
                print("This book:", self.Book.ExtendedAbbreviation, "next book:", None)
        while chapter.nextChapter != None and self.Book.ExtendedAbbreviation == chapter.nextChapter.Book.ExtendedAbbreviation:
            sleep(delay) # toggle so webserver doesn't get upset with us being a robot!
            chapter = BibleChapterExtract(book, chapter.nextChapter.Chapter, version=version, isDebug=self.isDebug)
            if self.isDebug:
                if chapter.nextChapter != None:
                    print("This book:", self.Book.ExtendedAbbreviation, "next book:", chapter.nextChapter.Book.ExtendedAbbreviation)
                else:
                    print("This book:", self.Book.ExtendedAbbreviation, "next book:", None)
        if chapter.nextChapter != None:
            self.nextBook = chapter.nextChapter.Book.Name
        # as book is now complete, mark it so
        self.makeComplete()
        # now remove any old ones
        self.deleteOldBooks()
        return

    @db_session
    def makeComplete(self):
        book = Book[self.Book.id]
        if self.isDebug:
            print("Mark book complete:", book.Name)
        book.IsComplete = True
        return

    @db_session
    def deleteOldBooks(self):
        book = Book[self.Book.id]
        version = book.version
        abbreviation = version.Abbreviation
        year = version.Year
        if self.isDebug:
            print("Deleting old books:", book.Name, book.ExtendedAbbreviation, abbreviation, "not year:", year)
        allVersions = select(v for v in Version if v.Abbreviation == abbreviation)[:]
        count = 0
        for otherVersion in allVersions:
            if otherVersion.Year != year:
                count += 1
                oldBook = Book.get(ExtendedAbbreviation = book.ExtendedAbbreviation, version = otherVersion)
                if self.isDebug:
                    print("Deleting old book:", book.Name, book.ExtendedAbbreviation, otherVersion.Abbreviation, otherVersion.Year)
                oldBook.delete()
        if self.isDebug and count == 0:
            print("No old books found")
        return


if __name__ == "__main__":
    """
    Test code while debugging.
    """
    # BibleBookExtract("mark", "NLT")
    # book = BibleBookExtract("john", "MSG")
    # BibleBookExtract("phil", "NIVUK")
    # book = BibleBookExtract("Revelation", "NIVUK", isDebug=True)
    book = BibleBookExtract("Genesis", "MSG", isDebug=True)
    print("Next book:", book.nextBook)
    print("Previous book:", book.prevBook)