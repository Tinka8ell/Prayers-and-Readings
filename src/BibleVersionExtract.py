# Process a bible version
#
#     Requires: 
#         Version abrieviation

from BibleStore import *
from BibleBookExtract import BibleBookExtract
from time import sleep

class BibleVersionExtract():
    """
    Process a bible version

        Requires: 
            Version abrieviation
    """

    def __init__(self, version="NIVUK", delay=1, isDebug=False):  # default to English NIV
        self.isDebug = isDebug
        bookDelay = 5 * delay # pause a little longer between books?
        extractDebug = self.isDebug
        book = BibleBookExtract("Mark", version=version, isDebug=extractDebug)
        if book.Book == None:
            if self.isDebug:
                print("Nothing done as all up to date")
        else: # actually did something
            self.versionId = book.Book.versionId
            if self.isDebug:
                print("Started with:", book.Book.Name)
            previous = book.prevBook

            # look forward
            while book.nextBook != None:
                sleep(bookDelay)
                book = BibleBookExtract(book.nextBook, version=version, isDebug=extractDebug)
                if self.isDebug:
                    print("Moving forward with:", book.Book.Name)

            # look backward
            while previous != None:
                sleep(bookDelay)
                book = BibleBookExtract(previous, version=version, isDebug=extractDebug)
                if self.isDebug:
                    print("Moving backward with:", book.Book.Name)
                previous = book.prevBook

            # as version is now complete, mark it so
            self.makeComplete()
            # now remove any old ones
            self.deleteOldVersions()
        return

    @db_session
    def makeComplete(self):
        version = Version[self.versionId]
        abbreviation = version.Abbreviation
        year = version.Year
        if self.isDebug:
            print("Mark version complete:", abbreviation, year)
        version.IsComplete = True
        return

    @db_session
    def deleteOldVersions(self):
        version = Version[self.versionId]
        abbreviation = version.Abbreviation
        year = version.Year
        versionId = version.id
        if self.isDebug:
            print("Deleting old versions:", abbreviation, "not year:", year)
        allVersions = select(v for v in Version if v.Abbreviation == abbreviation)[:]
        count = 0
        for otherVersion in allVersions:
            if otherVersion.id != versionId:
                count += 1
                if self.isDebug:
                    print("Deleting old version:", otherVersion.Abbreviation, otherVersion.Year)
                otherVersion.delete()
        if self.isDebug and count == 0:
            print("No old versions found")
        return


if __name__ == "__main__":
    """
    Test code while debugging.
    """
    # version = BibleVersionExtract("NLT", isDebug=True)
    version = BibleVersionExtract("MSG", isDebug=True)
    # version = BibleVersionExtract("NIVUK", isDebug=True)
