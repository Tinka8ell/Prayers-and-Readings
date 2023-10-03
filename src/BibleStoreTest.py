from BibleStore import *
from BiblePOPO import *

@db_session
def makeVersion():
    version = Version(Abbreviation = "TEST", Name = "Test version", Year = 2023, Copyright = "Copyright for TEST version in 2023")
    versionPOPO = VersionPOPO(Abbreviation = version.Abbreviation, Name = version.Name, Year = version.Year, Copyright = version.Copyright)
    versionPOPO.setId(version.id)
    return versionPOPO

@db_session
def getVersion(id=None, Abbreviation = None):
    version = None
    if id != None:
        version = Version.get(id=id)
    elif Abbreviation != None:
        versions = select(v for v in Version if v.Abbreviation == Abbreviation)[:]
        if len(versions) > 0:
            version = versions[0]
    if version != None:
        versionPOPO = VersionPOPO(Abbreviation = version.Abbreviation, Name = version.Name, Year = version.Year, Copyright = version.Copyright)
        versionPOPO.setId(version.id)
    else:
        versionPOPO = None
    return versionPOPO

@db_session
def makeBook(versionId):
    version = Version.get(id=versionId)
    print("Got version:", versionId, version.Abbreviation)
    book = Book(ExtendedAbbreviation = "1TES", Name = "1 Test Book", Total = 123, IsComplete = True, version = version)
    commit()
    print("Got book:", book.id, book.ExtendedAbbreviation)
    print("with version:", book.version.id, book.version.Abbreviation)
    bookPOPO = BookPOPO(book.Name)
    bookPOPO.setId(book.id)
    bookPOPO.setFields(book.Name, book.Total, book.IsComplete, book.version.id)
    return bookPOPO

@db_session
def getBook(id=None, Abbreviation = None, versionId = None):
    book = None
    if id != None:
        book = Book.get(id=id)
    elif Abbreviation != None and versionId != None:
        book = Book.get(ExtendedAbbreviation=Abbreviation, version=Version[versionId])
    if book != None:
        bookPOPO = BookPOPO(book.Name)
        bookPOPO.setId(book.id)
        bookPOPO.setFields(book.Name, book.Total, book.IsComplete, book.version.id)
    else:
        bookPOPO = None
    return bookPOPO


if __name__ == "__main__":
    """
    Test code while debugging.
    """
    versionName = "TEST"
    bookName = "1TES"

    print("Get Version ...", versionName)
    version = getVersion(Abbreviation=versionName)
    if version != None:
        print("Got test version:", version.Abbreviation, version.Year, version.IsComplete, version.Name, version.Copyright, version.id)
    else:
        print("Make Version ...")
        version = makeVersion()
        print("Made test version:", version.Abbreviation, version.Year, version.IsComplete, version.Name, version.Copyright, version.id)

    versionId = version.id
    print("Get Version ... ", versionId )
    version = getVersion(id=versionId)
    print("Got test version:", version.Abbreviation, version.Year, version.IsComplete, version.Name, version.Copyright, version.id)

    print("Get Book ...", bookName)
    book = getBook(Abbreviation=bookName)
    if book != None:
        print("Got test book:", book.ExtendedAbbreviation, book.Name, book.Total, book.IsComplete, book.id)
        print("    with version:", book.version.Abbreviation, book.version.Year, book.version.IsComplete, book.version.Name, book.version.Copyright, book.version.id)
    else:
        print("Make Book ...")
        book = makeBook(versionId)
        print("Made test book:", book.ExtendedAbbreviation, book.Name, book.Total, book.IsComplete, book.id)
        bookVersion = getVersion(id=book.versionId)
        print("     with version:", bookVersion.Abbreviation, bookVersion.Year, bookVersion.IsComplete, bookVersion.Name, bookVersion.Copyright, bookVersion.id)

    bookId = book.id
    print("Get Book ... ", bookId )
    book = getBook(id=bookId)
    print("Got test book:", book.ExtendedAbbreviation, book.Name, book.Total, book.IsComplete, book.id)
    bookVersion = getVersion(id=book.versionId)
    print("     with version:", bookVersion.Abbreviation, bookVersion.Year, bookVersion.IsComplete, bookVersion.Name, bookVersion.Copyright, bookVersion.id)

