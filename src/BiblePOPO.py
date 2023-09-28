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
    
    def __init__(self, ExtenedAbbreviation, Name) -> None:
        self.ExtenedAbbreviation = ExtenedAbbreviation
        self.Name = Name
        return

