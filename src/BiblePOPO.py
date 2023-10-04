# Bible POPO (Plain Old Python Objects) contains the data we will need to extract 
# to create the BibleStore objects and data

class CanHaveId():
    
    def __init__(self) -> None:
        self.id = None
        return
    
    def setId(self, id):
        self.id = id
        return


class VersionPOPO(CanHaveId):
    
    def __init__(self, Abbreviation, Name="Was not set", Year=0, Copyright=None, IsComplete=False) -> None:
        super()
        self.Abbreviation = Abbreviation
        self.Name = Name
        self.Year = Year
        self.Copyright = Copyright
        self.IsComplete = IsComplete
        return


def _abbreviateBookName(name):
    """
    Consider 1st 5 characters, less trailing spaces as an alternative.
    Could add a "look-up" for books, matching key + "*" if only one exisit 
       or first found (not so good!)
    """
    abbreviation = name.strip()[0:3].lower()
    if abbreviation == 'phi': # as it is ambiguous, make it longer
        abbreviation = name.strip()[0:5].lower() # allow for "Philemon" instead of "Philipians"!
    if abbreviation == 'jud': # as it is ambiguous, make it longer
        abbreviation = name.strip()[0:4].lower() # allow for "Judges" instead of "Jude"!
    return abbreviation

class BookPOPO(CanHaveId):
    
    def __init__(self, Name) -> None:
        super()
        book = Name.strip()
        abbreviation = book[0:1]
        if abbreviation.isdigit():
            abbreviation += " " + _abbreviateBookName(book[1:])
        else:
            abbreviation = _abbreviateBookName(book)
        self.ExtendedAbbreviation = abbreviation
        self.Name = Name
        self.Total = 0
        self.IsComplete = False
        self.versionId = None
        return
    
    def setFields(self, Name, Total, IsComplete, versionId):
        self.Name = Name
        self.Total = Total
        self.IsComplete = IsComplete
        self.versionId = versionId
        return


class ChapterPOPO(CanHaveId):
    
    def __init__(self, Name=None, Book=None, Chapter=0, Verses=0, IsComplete=False) -> None:
        super()
        self.Verses = Verses
        self.IsComplete = IsComplete
        if Name == None:
            self.Chapter = Chapter
            self.Name = Book + " " + str(Chapter)
            self.Book = BookPOPO(Book)
        else:
            self.Name = Name
            parts = Name.split()
            self.Chapter = int(parts[-1])
            self.Book = BookPOPO(" ".join(parts[0:-1]))
        self.Number = self.Chapter
        return

