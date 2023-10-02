# Bible POPO (Plain Old Python Objects) contains the data we will need to extract 
# to create the BibleStore objects and data

class VersionPOPO():
    
    def __init__(self, Abbreviation, Name="Was not set", Year=0, Copyright=None) -> None:
        self.Abbreviation = Abbreviation
        self.Name = Name
        self.Year = Year
        self.Copyright = Copyright
        return


class BookPOPO():
    
    def __init__(self, Name) -> None:
        book = Name.strip()
        abbreviation = book[0:1]
        if abbreviation.isdigit():
            abbreviation += " " + book[1:].strip()[0:3].lower()
        else:
            abbreviation = book[0:3].lower()
        self.ExtenedAbbreviation = abbreviation
        self.Name = Name
        return


class ChapterPOPO():
    
    def __init__(self, Name=None, Book=None, Chapter=0) -> None:
        if Name == None:
            self.Chapter = Chapter
            self.Name = Book + " " + str(Chapter)
            self.Book = BookPOPO(Book)
        else:
            self.Name = Name
            parts = Name.split()
            self.Chapter = int(parts[-1])
            self.Book = BookPOPO(" ".join(parts[0:-1]))
        return

