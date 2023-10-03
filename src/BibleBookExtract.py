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

    def __init__(self, book, version="NIVUK"):  # default to English NIV
        chapter = BibleChapterExtract(book, 1, version=version, isDebug=True)
        if chapter:
            self.Book = chapter.bibleStoreBook
            while self.Book == chapter.bibleStoreBook:
                chapter = BibleChapterExtract(book, chapter.nextChapter.Chapter, version=version)
            # as book is now complete, mark it so
            self.makeComplete()
        return

    @db_session
    def makeComplete(self):

        return


if __name__ == "__main__":
    """
    Test code while debugging.
    """
    BibleBookExtract("mark", "NLT")
    # BibleBookExtract("john", "MSG")
    # BibleBookExtract("phil", "NIVUK")
    # BibleBookExtract("Revelation", "NIVUK")
