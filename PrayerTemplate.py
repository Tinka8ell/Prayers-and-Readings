# parse html

from datetime import date, timedelta, datetime, time
import os
from pathlib import Path

from dateutil.parser import parse

from BibleReading import BibleReading, cleanText, tagText
from DailyPrayer import DailyPrayer
from Moravian import Moravian
from OpenDoors import OpenDoors
from bs4 import BeautifulSoup # used to parse values in an html file


def tagDay(prefix, day, suffix):
    html = tagText(prefix + day + suffix,
                   'a href="./' + day + '.html"')
    return html


class PrayerTemplate():

    def __init__(self, name, version="NIVUK"):  # default to English NIV
        self.version = version
        self.name = name
        self.p1 = '''<!DOCTYPE html>
<html>
    <head>
        <title>'''
        self.p2a = '''
        </title>
        <meta name="filedate" content="'''
        self.p2b = '''">
        <meta name="color-scheme" content="light dark">
        <meta name="supported-color-schemes" content="light dark">
        <link rel="stylesheet" type="text/css" href="/style/style.css">
    </head>
    <body>'''
        self.p3 = '''</body>
</html>'''
        self.moravian = "https://www.moravian.org/the-daily-texts/"
        self.opendoors = "https://www.opendoorsuk.org/persecution/world-watch-list/"
        # note that we only need the daily part of the prayer so could use evening or morning ...
        self.northumbrian = "https://www.northumbriacommunity.org/offices/morning-prayer/"
        self.paras = []
        self.title = None
        self.addDate = False
        self.weekLink = None
        self.documentDate = datetime.today() # document is now, unless contents are older ..
        self.oldDocumentDate = datetime.today() # the same for now
        self.parse()
        return

    def parse(self):
        directory = os.path.dirname(__file__)
        parent = directory  # keep finger on parent
        name = self.name
        filename = os.path.join(directory, name + ".txt")
        self.templateDate = datetime.fromtimestamp(os.path.getmtime(filename)) # get a date for template last update
        with open(filename, 'r', encoding="utf-8") as f:
            line = f.readline()
            while line:
                paraType = ""
                if line[1] == ".":
                    paraType = line[0]
                    line = line[2:].strip()
                if paraType == "B":
                    line = line.split(" - ")[0].strip()
                elif paraType == "U":
                    pos = line.index("http")
                    tag = line[0: pos].strip()
                    url = line[pos:].strip()
                    line = (tag, url)
                elif paraType == "I":
                    self.addDate = True
                elif paraType == "D":
                    self.addDate = True
                elif paraType == "T":
                    self.title = line
                if paraType != "#":  # ignore commented lines
                    self.paras.append((paraType, line))
                line = f.readline()
        return

    def closeTag(self):
        html = ""
        if self.closingTag != "":
            html = self.closingTag
            self.closingTag = ""
        return html

    def openTag(self, tag, para):
        # print("OpenTag:", tag, para, self.closingTag)
        isNotBr = True
        html = ""
        if tag == "br":
            if self.closingTag == "</p>":
                tag = "<br/>"
                isNotBr = False
            else:
                tag = "p"
        if isNotBr:
            html = self.closeTag()
            self.closingTag = "</" + tag + ">"
            tag = "<" + tag + ">"
        html += tag + cleanText(para, xmlReplace=True)
        # print("OpenTag -", tag, self.closingTag, isNotBr)
        return html

    def getFilename(self, directory=None):
        if not directory:
            # get the name of our directory
            directory = os.path.dirname(__file__)
        parent = directory  # keep finger on parent
        directory = os.path.join(directory, "prayers")
        if not os.path.exists(directory):
            os.mkdir(directory)
        name = self.name
        if self.addDate:
            name += date.today().isoformat()
        filename = os.path.join(directory, name + ".html")
        if os.path.exists(filename):
            self.oldDocumentDate = datetime.fromtimestamp(os.path.getmtime(filename)) # last update time of previous file
            # see if file has an internal time
            with open(filename) as fp:
                soup = BeautifulSoup(fp, 'html.parser')
                # <meta name="filedate" content="2022-01-03T10:44:49Z">
                tag = soup.find('meta', 'name=filedate') # get the filedate meta tag
                if tag is not None:
                    self.oldDocumentDate = date(tag['content'])
        # print("Creating prayer page:", filename)
        title = "Template for: " + date.today().strftime("%A %d %B %Y")
        if self.title is None:
            self.title = title
        return filename, parent

    def html(self, directory=None):
        filename, parent = self.getFilename(directory)
        print("Creating html: filename =", filename)
        html = self.getHtml()
        # only create new version if it really is new ...
        print("Creating html: oldDocumentDate =", self.oldDocumentDate, ", documentDate =", self.documentDate)
        if self.oldDocumentDate < self.documentDate:
            # use the new one
            ### print("Writing ", filename, self.oldDocumentDate , self.documentDate)
            with open(filename, 'w', encoding="utf-8") as f:
                print(html, file=f)
            # may remove this when we have proper redirect working
            if os.name == 'posix':
                # point symbolic link to file created:
                symbolic = os.path.join(parent, self.name + ".html")
                print("Creating symbolic link: symbolic =", symbolic)
                filename = Path(filename)
                print("Creating symbolic link: filename =", filename)
                symbolic = Path(symbolic)
                print("Creating symbolic link: symbolic =", symbolic)
                if symbolic.exists():
                    os.unlink(symbolic)
                os.symlink(filename, symbolic)
        else:
            ### print("Skipping ", filename, self.oldDocumentDate , self.documentDate)
            pass
        return

    def updateDocumentDate(self, newDate):
        # start with date objects
        ### print("updateDocumentDate:", documentDate, newDate)
        now = datetime.today().date()
        if now.day != newDate.day: # so not from today
            ### print("now > newDate:", now, newDate)
            # now work with datetime objects
            newDatetime = datetime.combine(newDate, time()) # start of newDate as time() is 0:00:00!
            if self.documentDate > newDatetime: # if older than current document date
                ### print("documentDate > newDate:", documentDate, newDate)
                self.documentDate = newDatetime
        ### print("updateDocumentDate sets:", documentDate)
        return

    def getHtml(self):
        self.documentDate = self.templateDate # start with the age of the template
        html = []
        html.append(self.p1)
        html.append(self.title)
        fileDatePos = (len(html), len(self.p2a)) #where to add the iso date
        html.append(self.p2a + self.p2b)
        # html.append(tagText(self.title, "h1"))
        self.closingTag = ""
        for paraType, para in self.paras:
            if paraType == "B":  # Bible passage
                html.append(self.closeTag())
                bible = BibleReading(para, self.version)
                html.append(bible.getHtmlParas(reading=True))
            elif paraType == "":  # line break
                html.append(self.openTag("br", para))
            elif paraType == "P":  # paragraph
                html.append(self.openTag("p", para))
            elif paraType == "U":  # URL - link
                html.append(self.openTag("p", '<a href="' +
                             para[1] + '">' + para[0] + "</a>"))
            elif paraType == "S":  # strong - bold
                html.append(self.openTag("p", "<b>" + para + "</b>"))
            elif paraType == "H":  # heading
                html.append(self.openTag("h2", para))
            elif paraType == "T":  # title
                html.append(self.openTag("h1", para))
            elif paraType == "D":  # date
                dateFormat = "%A %d %B %Y"
                if para and para != "":
                    dateFormat = para
                html.append(self.openTag("h2", date.today().strftime(dateFormat)))
            elif paraType == "W":  # link to previous and next week days
                if not self.weekLink:
                    dateFormat = "%A"
                    if para and para != "":
                        dateFormat = para
                    day1 = timedelta(days=1)
                    thisDay = date.today()
                    count = 1
                    while thisDay.strftime(dateFormat) != self.name:
                        thisDay = thisDay + day1
                        if count > 7:
                            raise ValueError()
                        count += 1
                    self.weekLink = '<div class="left">'
                    yesterday = (thisDay - day1).strftime(dateFormat)
                    self.weekLink += tagDay('<<<<< ', yesterday, '')
                    self.weekLink += '</div><br/><div class="right">'
                    tomorrow = (thisDay + day1).strftime(dateFormat)
                    self.weekLink += tagDay('', tomorrow, ' >>>>>')
                    self.weekLink += "</div>"
                html.append(self.openTag("p", self.weekLink))
            elif paraType == "I":  # Insert from another page
                html.append(self.closeTag())
                if para == "Moravian":
                    insert = Moravian(self.moravian, version=self.version)
                    self.updateDocumentDate(insert.getDate())
                    # print("Moravian:", insert.show())
                    html.append(insert.getHtml(showdivs=False))
                elif para == "Northumbrian":
                    insert = DailyPrayer(self.northumbrian, version=self.version)
                    self.updateDocumentDate(insert.getDate())
                    # print("DailyPrayer:", insert.show())
                    html.append(insert.getHtml(showdivs=False))
                elif para == "OpenDoors":
                    insert = OpenDoors(self.opendoors)
                    self.updateDocumentDate(insert.getDate())
                    # print("DailyPrayer:", insert.show())
                    html.append(insert.getHtml(showdivs=False))
            else:
                print("unknown para type:", paraType)
        html.append(self.closeTag())
        html.append(self.p3)
        # insert document date
        pos, index = fileDatePos
        # set this document's date
        html[pos] = html[pos][:index] + self.documentDate.isoformat() + html[pos][index:]
        return '\n'.join(html)


if __name__ == "__main__":
    import sys
    argv = sys.argv
    # testing parameters:
    # argv = ["testing", "Wednesday", "Thursday", "Friday"]
    # argv = ["testing", "midday"]
    if len(argv) > 1:
        for name in argv[1:]:
            # print("Processing:", name)
            if name.endswith(".txt"):
                name = name[0:-4]
                # print("Processing:", name)
            if name not in ("Upload", "weekly"): # don't exclude:  , "Morning", "Evening"):
                prayer = PrayerTemplate(name, version="NLT")
                prayer.html(directory="/var/www/html")
            else:
                # print("skipping", name)
                pass
    else:
        for name in ("Morning", "Evening"):
            # print("Processing:", name)
            prayer = PrayerTemplate(name, version="NLT")
            prayer.html(directory="/var/www/html")
