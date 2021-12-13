# parse html

from datetime import date
from enum import Enum, auto
import os
from pathlib import Path

from bs4 import NavigableString
from dateutil.parser import parse

from BibleReading import BibleReading, cleanText, tagText
from WebTree import WebTree


def isStrong(nextP):
    return nextP.name == "strong" or nextP.name == "b"


class State(Enum):
    SKIPPING = auto()
    PROCESSING_READINGS = auto()
    READING_TITLE = auto()
    PROCESSING_MEDITATION = auto()


class DailyPrayer(WebTree):
    """
    Grab the verses and meditation from the daily prayer
    of the Nothumbrian Community.
    """

    def __init__(self, url, version="NIVUK"):  # default to English NIV
        self.version = version
        super().__init__(url)
        self.p1 = '''<!DOCTYPE html>
<html>
    <head>
        <title>'''
        self.p2 = '''
        </title>
        <meta name="color-scheme" content="light dark">
        <meta name="supported-color-schemes" content="light dark">
        <link rel="stylesheet" type="text/css" href="/style/style.css">
    </head>
    <body>'''
        self.p3 = '''</body>
</html>'''
        return


    def parseContents(self, nextP, indent, parentIsStrong=False):
        # parentIsStrong is used for extra inner wrapping of strong (or bold) text
        if isinstance(nextP, NavigableString):
            # print(indent, "NavigableString: state=", self.state)
            if self.state != State.SKIPPING:
                # ## print(indent, "Child (text):", nextP.string)
                pass
            # tidy up text before we append it
            text = nextP.string
            self.text += " " + cleanText(text)
        else:
            # print(indent, "Other NextP: state=", self.state)
            if self.state != State.SKIPPING:
                # ## print(indent, "Child (" + nextP.name + "):")
                pass
            if nextP.name == "h2":
                if self.state == State.PROCESSING_READINGS:
                    self.state = State.READING_TITLE
                if self.state == State.SKIPPING:
                    # ## print("Starting real parse")
                    self.state = State.PROCESSING_READINGS
                if self.state == State.PROCESSING_MEDITATION:
                    # ## print("Ending real parse")
                    self.state = State.SKIPPING
                self.text = ""  # start new text
            if self.state == State.PROCESSING_READINGS:
                # print(nextP.prettify())
                # only interested in the h2 and strong
                if nextP.name == "strong":
                    self.text = ""
            elif self.state == State.PROCESSING_MEDITATION:
                if nextP.name == "br":  # treat br's as line breaks
                    self.text += "\n"
            ### do any children ###
            for child in nextP.children:
                self.parseContents(child, indent + "   ", parentIsStrong=isStrong(nextP))
            ### process the end of tags ###
            ignore = ("div", "sup", "br", "article")
            if self.state == State.READING_TITLE:
                ignore = ("div", "sup", "br", "em", "article")
            if nextP.name not in ignore:
                text = self.text.strip()
                if self.state == State.PROCESSING_READINGS:
                    # parsing scripture references
                    if nextP.name == "h2":
                        # ## print("Reading Heading:", text)
                        self.daily.append(text)
                    elif isStrong(nextP) or parentIsStrong:
                        if len(text) > 0:  # ignore blank lines
                            if not self.date:  # not yet checked the day
                                pageDate = text
                                datetime = parse(pageDate)
                                self.date = datetime.date()
                                # check if showing today's date
                                today = date.today()
                                self.isToday = today == datetime.date()
                                # ## print("Date:", pageDate, datetime, self.date, self.isToday)
                            else:  # get the scripture passage
                                # print(indent, "Scripture:", text)
                                self.daily.append(text)
                        '''else:
                            print(indent, "Blank bold")
                        '''
                    else:
                        # print(indent, "Ignoring:", nextP)
                        pass  # ignore all else (including "p")
                elif self.state != State.SKIPPING:
                    # parsing meditation
                    if nextP.name == "h2":
                        # ## print("Meditation Heading:", text)
                        self.meditation.append(("H", text))  # heading
                    elif nextP.name == "h3" or nextP.name == "strong":
                        # ## print("Sub-heading:", text)
                        self.meditation.append(("T", text))  # sub-heading
                    elif nextP.name == "em":
                        if len(text) > 40:
                            # not really an author name, treat as paragraph
                            # ## print("Paragraph:", nextP.name, text)
                            self.meditation.append(("P", text))  # paragraph
                        else:
                            # ## print("Author:", text)
                            self.meditation.append(("A", text))  # author
                    else:
                        # ## print("Paragraph:", nextP.name, text)
                        self.meditation.append(("P", text))  # paragraph
                if nextP.name == "h2":
                    if self.state == State.READING_TITLE:
                        self.state = State.PROCESSING_MEDITATION
                self.text = ""
        return

    def parse(self):
        '''
        Bit we want is the entry-content:
        Skip to first <h2> - scripture readings
        First Para of the first para is date
        Next paras are:
           <strong> reference
           or text
        Skip to second <h2> - meditation
        Next paras are:
           <strong/h3> title
           <em> author
           or text
        '''
        # print(self.root.prettify()) # debug
        self.daily = []  # place for readings
        self.isToday = None  # so we can check it is today's readings
        self.date = None  # for formatting the date
        self.meditation = []  # place for the meditation
        self.text = ""  # place to build text strings as we parse
        self.state = State.SKIPPING  # initial state is to ignore till first "h2"
        mainContent = self.root.find('div', id="main-content")
        self.parseContents(mainContent, "")
        return

    def show(self):
        super().show()
        print("version:", self.version)
        print("date:", self.date)
        print("today?:", self.isToday)
        print("daily:", self.daily)
        print("meditation:", self.meditation)
        return

    def showDaily(self):
        print("Daily:")
        for passage in self.daily:
            bible = BibleReading(passage, self.version)
            bible.showPassage()
        for para in self.meditation:
            if para[0] == "T":
                print("Title:", para[1])
            elif para[0] == "A":
                print("Author:", para[1])
            else:
                print(para[1])
        return

    def saveDaily(self, directory=None):
        if not directory:
            # get the name of our directory
            directory = os.path.dirname(__file__)
        parent = directory  # keep finger on parent
        name = "prayers"
        directory = os.path.join(directory, name)
        if not os.path.exists(directory):
            os.mkdir(directory)
        date = self.date.isoformat()
        filename = os.path.join(directory, date + ".html")
        # print("Creating daily reading page:", filename)
        title = "Daily prayer readings for: " + \
            self.date.strftime("%A %d %B %Y")
        with open(filename, 'w', encoding="utf-8") as f:
            print(self.p1, file=f)
            print(title, file=f)
            print(self.p2, file=f)
            print("<h1>" + title + "</h1>", file=f)
            self.html(f)
            print(self.p3, file=f)
        if os.name == 'posix':
            # point symbolic link to file created:
            symbolic = os.path.join(parent, name + ".html")
            filename = Path(filename)
            symbolic = Path(symbolic)
            if symbolic.exists():
                os.unlink(symbolic)
            os.symlink(filename, symbolic)
        return

    def htmlReading(self, passage, f, tag=None, showdivs=False):
        # override and force no Tag:
        tag = None
        bible = BibleReading(passage, self.version)
        if tag:
            print(tagText(passage, tag), file=f)
            bible.htmlParas(f)
        else:
            bible.htmlParas(f, reading=True)
        if showdivs:
            print("<hr/>", file=f)
        return

    def html(self, f, showdivs=True):
        '''
        for line in self.daily:
           print("daily:", line)
        '''
        print(tagText(self.daily[0], "h2"), file=f)
        for passage in self.daily[1:]:
            # print(f"'{passage}'")
            self.htmlReading(passage, f, tag="h3", showdivs=showdivs)
        for paraType, para in self.meditation:
            # ## print("type", paraType, "para", para)
            if paraType == "H":
                print(tagText(para, "h2"), file=f)
            elif paraType == "T":
                print(tagText(para, "h3"), file=f)
            elif paraType == "A":
                print(tagText(para, 'p class="author"'), file=f)
            else:
                prefix = "<p>"
                for p in para.split("\n"):
                    print(prefix + cleanText(p, xmlReplace=True), file=f)
                    prefix = "<br/>"
                print("</p>", file=f)
        if showdivs:
            print("<hr/>", file=f)
        return


if __name__ == "__main__":
    day = DailyPrayer(
        "https://www.northumbriacommunity.org/offices/morning-prayer/", version="NLT")
    '''
   day.show()
   day.showDaily()
   print()
   '''
    day.saveDaily(directory="/var/www/html")
