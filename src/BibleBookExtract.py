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

    def __init__(self, book, version="NIVUK", isDebug=False):  # default to English NIV
        self.isDebug = isDebug
        self.nextBook = None
        self.prevBook = None
        chapter = BibleChapterExtract(book, 1, version=version, isDebug=self.isDebug)
        if chapter:
            if chapter.prevChapter != None:
                self.prevBook = chapter.prevChapter.Book.Name
            self.Book = chapter.bibleStoreBook
            if self.isDebug:
                if chapter.nextChapter != None:
                    print("This book:", self.Book.ExtendedAbbreviation, "next book:", chapter.nextChapter.Book.ExtendedAbbreviation)
                else:
                    print("This book:", self.Book.ExtendedAbbreviation, "next book:", None)
            while chapter.nextChapter != None and self.Book.ExtendedAbbreviation == chapter.nextChapter.Book.ExtendedAbbreviation:
                chapter = BibleChapterExtract(book, chapter.nextChapter.Chapter, version=version, isDebug=self.isDebug)
                if self.isDebug:
                    if chapter.nextChapter != None:
                        print("This book:", self.Book.ExtendedAbbreviation, "next book:", chapter.nextChapter.Book.ExtendedAbbreviation)
                    else:
                        print("This book:", self.Book.ExtendedAbbreviation, "next book:", None)
            # as book is now complete, mark it so
            self.makeComplete()
            if chapter.nextChapter != None:
                self.nextBook = chapter.nextChapter.Book.Name
        return

    @db_session
    def makeComplete(self):
        book = Book[self.Book.id]
        if self.isDebug:
            print("Mark book complete:", book.Name)
        book.IsComplete = True
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