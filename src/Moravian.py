# process Moravian daily readings
'''
import urllib.request # as Request
# used to parse values into the url
import urllib.parse
from bs4 import BeautifulSoup
'''
from datetime import date
import os
from pathlib import Path
import re

from dateutil.parser import parse

from BibleReading import BibleReading, tagText
from WebTree import WebTree


def removeSemis(text):
    return text.replace(" ;", "").replace("  ", " ").strip()


class Moravian(WebTree):

    def __init__(self, url, version="NIVUK"):  # default to English NIV
        self.version = version
        self.prefix = "/"
        super().__init__(url)
        self.p1 = '''<!DOCTYPE html>
<html>
<head>
<title>'''
        self.p2 = '''</title>
<link rel="stylesheet" type="text/css" href="/style/style.css">
</head>
<body>'''
        self.p3 = '''</body>
</html>'''
        return

    def parse(self):
        '''
        Bit we want is the textwidget:
        First Para is date
        Next is Div with everything else:
        Optional Watchword paras:
        ... after dash is verse with reference - no link
        Optional special day with readings after dash
        Daily readings with date dash and readings
        Next is paras with links including reference
        Next is para of prayer with no links
        End of div
        other stuff
        End of div (textwidget)
        '''
        if self.root == None:
            raise Exception("*** Error getting web page for " + self.url + " ***")  
        textwidget = self.root.find('div', class_="textwidget")
        if textwidget == None:
            raise Exception("*** Error finding textwidget in page for " + self.url + " ***")
        # print(textwidget.prettify()) # debug
        # first para is date, so get the string and convert
        pageDate = textwidget.p.string
        try:
            datetime = parse(pageDate)
            self.date = datetime.date()
        except:
            self.date = date(year=2020, month=1, day=1)
        # check if showing today's date
        today = date.today()
        self.isToday = today.day == self.date.day
        # get first para of next div
        nextP = textwidget.div.p
        # work through each pars to see what it is
        watchwords = []
        daily = []
        oneYear = []
        prayer = None
        while nextP:
            # get all text, add semicolon delimiters:
            text = ""
            for string in nextP.stripped_strings:
                text += " ; " + str(string)
            # get link if one
            a = nextP.find('a')
            # test if optional watchword:
            # print("nextP", a, text) # debug
            pos = text.find("Watchword")
            pClass = nextP.get('class', "")  # Nothing if no class attribute
            if pos >= 0:
                # ## print("Found watchword")
                # record watch word
                text = text[pos:]  # get rest
                strings = text.split('—', 1)
                if len(strings) == 1:
                    strings = text.split('–', 1)
                # add description and text
                # remove any extra semicolons and double spaces
                description = removeSemis(strings[0])
                text = removeSemis(strings[1])
                # ## need to extract passage from end ...
                regEx = "([a-zA-Z0-9 ]+\\d+ *(: *(\\d+[ ,-])*\\d+)([ ,-]*\\d+ *(: *(\\d+[ ,-])*\\d+))*)$"
                passage = re.search(re.compile(regEx), text)
                if passage:
                    passage = passage.group().strip()
                watchwords.append((description, text, passage))
                if description.casefold().find("for the Week".casefold()) > 0:
                    # save a copy for the rest of the week.
                    # get the name of our directory
                    directory = os.path.dirname(__file__)
                    filename = os.path.join(directory, "weekly.txt")
                    with open(filename, 'w', encoding="utf-8") as f:
                        print(description, file=f)
                        print(text, file=f)
                        print(passage, file=f)
            elif a:
                # ## print("Found link", nextP.prettify())
                # if link then have one of today's readings
                reading = nextP.a.string.strip()
                while len(reading) > 0 and reading[-1].isalpha():
                    # print("reading:", reading)
                    reading = reading[:-1]
                if len(reading) <= 0:  # not there, try whole paragraph
                    reading = " ".join(nextP.stripped_strings)
                    while len(reading) > 0 and reading[-1].isalpha():
                        # print("reading:", reading)
                        reading = reading[:-1]
                    regEx = "([a-zA-Z0-9 ]+\\d+ *(: *(\\d+[ ,-])*\\d+)([ ,-]*\\d+ *(: *(\\d+[ ,-])*\\d+))*) *[A-Z]*$"
                    passage = re.search(re.compile(regEx), reading)
                    if passage:
                        # if we found a passage it was a reading
                        reading = passage.group(1).strip()
                # print("daily.append(reading.strip()):", reading.strip())
                daily.append(reading.strip())
            else:
                # either prayer or passages for year (or special day)
                # ## print("Found other", nextP.prettify())
                sep = ' — '
                strings = text.split(sep, 1)
                if len(strings) == 1:
                    sep = ' – '
                    strings = text.split(sep, 1)
                # print(f"Check for prayer: class = {pClass}, len(strings) = {len(strings)} and not ('p1' in pClass) = {not ('p1' in pClass)}")
                if (not ("p1" in pClass)) and len(strings) == 1:
                    # print(f"Found prayer? class = {pClass}")
                    # no split so prayer
                    if len(watchwords) > 0 or len(daily) > 0 or len(oneYear) > 0:
                        # must have one of these first to be a prayer ...
                        if prayer:
                            # if already had prayer check if it was a reading for today ...
                            # print("Previous prayer:", prayer)
                            text = removeSemis(prayer)
                            # print("As text:", text)
                            regEx = "([a-zA-Z0-9 ]+\\d+ *(: *(\\d+[ ,-])*\\d+)([ ,-]*\\d+ *(: *(\\d+[ ,-])*\\d+))*) *[A-Z]*$"
                            passage = re.search(re.compile(regEx), text)
                            if passage:
                                # if we found a passage it was a reading
                                # just take the passage, and not the optional version
                                passage = passage.group(1).strip()
                                # print("Found daily reading")
                                # print("daily.append(passage):", passage)
                                daily.append(passage)
                                prayer = None  # remove from prayer
                            else:
                                # must be another para - may be prayer and history ...
                                pass
                        # remove any extra semicolons and double spaces
                        text = removeSemis(strings[0])
                        if prayer:
                            text = prayer + " \n " + text  # join to paragraphs
                        prayer = text
                else:
                    # print(f"Found passages - class = {pClass}")
                    # get passages
                    # remove any extra semicolons and double spaces
                    named = ""
                    if len(strings) > 1:
                        named = removeSemis(strings[0])
                        strings = strings[1:]
                    text = strings[0].strip()
                    strings = text.split(";")
                    passages = []
                    for string in strings:
                        passages.append(string.strip())
                    oneYear.append((named, passages))
            # move to next para
            nextP = nextP.find_next_sibling("p")
        if len(watchwords) == 0:
            # get the name of our directory
            directory = os.path.dirname(__file__)
            filename = os.path.join(directory, "weekly.txt")
            if os.path.exists(filename):
                with open(filename, 'r', encoding="utf-8") as f:
                    description = f.readline()
                    text = f.readline()
                    passage = f.readline()
                    watchwords.append((description, text, passage))
        self.daily = daily
        self.prayer = prayer
        self.watchwords = watchwords
        self.oneYear = oneYear
        return

    def show(self):
        super().show()
        print("version:", self.version)
        print("date:", self.date)
        print("today?:", self.isToday)
        print("watchwords:", self.watchwords)
        print("one year:", self.oneYear)
        print("daily:", self.daily)
        print("prayer:", self.prayer)
        return

    def showDaily(self):
        print("Daily:")
        for passage in self.daily:
            bible = BibleReading(passage, self.version)
            bible.showPassage()
        print(self.prayer)
        return

    def saveDaily(self, directory=None):
        if not directory:
            # get the name of our directory
            directory = os.path.dirname(__file__)
        parent = directory  # keep finger on parent
        directory = os.path.join(directory, "daily")
        if not os.path.exists(directory):
            os.mkdir(directory)
        date = self.date.isoformat()
        filename = os.path.join(directory, date + ".html")
        # print("Creating daily reading page:", filename)
        title = "Moravian daily readings for: " + \
            self.date.strftime("%A %d %B %Y")
        with open(filename, 'w', encoding="utf-8") as f:
            print(self.p1, file=f)
            print(title, file=f)
            print(self.p2, file=f)
            print("<h1>" + title + "</h1>", file=f)
            self.html(f)
            print('<p><a href="year.html">' +
                  "Today's bible in a year readings</a></p>", file=f)
            print("<hr/>", file=f)
            print(self.p3, file=f)
        if os.name == 'posix':
            # point symbolic link to file created:
            symbolic = os.path.join(parent, "day.html")
            filename = Path(filename)
            symbolic = Path(symbolic)
            if symbolic.exists():
                os.unlink(symbolic)
            os.symlink(filename, symbolic)
        return

    def htmlReading(self, passage, f, tag=None, showdivs=False):
        html = self.getHtmlReading(passage, tag, showdivs)
        print(html, file=f)
        return

    def getHtmlReading(self, passage, tag=None, showdivs=False):
        html = []
        # force no Tag:
        tag = None
        bible = BibleReading(passage, self.version)
        if tag:
            html.append(tagText(passage, tag))
            html.append(bible.getHtmlParas())
        else:
            html.append(bible.getHtmlParas(reading=True))
        if showdivs:
            html.append("<hr/>")
        return '\n'.join(html)

    def html(self, f, showdivs=True):
        html = self.getHtml(showdivs)
        print(html, file=f)
        return

    def getDate(self):
        return self.date

    def getHtml(self, showdivs=True):
        html = []
        if len(self.watchwords) > 0:
            html.append("<h2>Watchwords</h2>")
            for word in self.watchwords:
                html.append(tagText(word[0], "h3"))
                if word[2]:
                    passage = word[2]
                    html.append(self.getHtmlReading(passage, tag="h4"))
                else:
                    html.append(tagText(word[1], "p"))
            if showdivs:
                html.append("<hr/>")
        # print(len(self.daily), "passages")
        for passage in self.daily:
            # print(f"'{passage}'")
            html.append(self.getHtmlReading(passage, tag="h3", showdivs=showdivs))
        html.append(tagText("Prayer", "h3"))
        if self.prayer:
            paras = self.prayer.split("\n")  # in case separate paragraphs
            for para in paras:  # should be at least one!
                html.append(tagText(para, "p"))
        if showdivs:
            html.append("<hr/>")
        return '\n'.join(html)

    def showWatchwords(self):
        if len(self.watchwords) == 0:
            print("No watchwords")
            return
        print("Watchwords:")
        for word in self.watchwords:
            print("Watchword:", word[0])
            print("Passage", word[1])
        return

    def showOneYear(self):
        if len(self.oneYear) == 0:
            print("No readings")
            return
        print("Bible in year:")
        for group in self.oneYear:
            print("Reason:", group[0])
            for passage in group[1]:
                print("Passage:", passage)
                bible = BibleReading(passage, self.version)
                bible.showPassage()
        return

    def saveYear(self, directory=None):
        if len(self.oneYear) == 0:
            return
        if not directory:
            # get the name of our directory
            directory = os.path.dirname(__file__)
        parent = directory  # keep finger on parent
        directory = os.path.join(directory, "year")
        if not os.path.exists(directory):
            os.mkdir(directory)
        date = self.date.isoformat()
        filename = os.path.join(directory, date + ".html")
        # ## print("Creating bible in year page:", filename)
        title = "Bible in a year for: " + self.date.strftime("%A %d %B %Y")
        with open(filename, 'w', encoding="utf-8") as f:
            print(self.p1, file=f)
            print(title, file=f)
            print(self.p2, file=f)
            print(tagText(title, "h1"), file=f)
            for group in self.oneYear:
                print(tagText(group[0], "h2"), file=f)
                for passage in group[1]:
                    print(tagText(passage, "h3"), file=f)
                    bible = BibleReading(passage, self.version)
                    bible.htmlParas(f)
                    print("<hr/>", file=f)
            print('<p>' + tagText("Today's daily readings",
                                  'a href="/day.html"') + "</p>", file=f)
            print("<hr/>", file=f)
            print(self.p3, file=f)
        if os.name == 'posix':
            # point symbolic link to file created:
            symbolic = os.path.join(parent, "year.html")
            filename = Path(filename)
            symbolic = Path(symbolic)
            if symbolic.exists():
                os.unlink(symbolic)
            os.symlink(filename, symbolic)
        return

    def webSave(self, directory=None):
        if not directory:
            # get the name of our directory
            directory = os.path.dirname(__file__)
        self.saveDaily(directory=directory)
        self.saveYear(directory=directory)
        year = os.path.join(directory, "year")
        day = os.path.join(directory, "daily")
        days = os.listdir(day)
        years = os.listdir(year)
        days = sorted(days, reverse=True)
        years = sorted(years, reverse=True)
        day5 = days[:5]
        year5 = years[:5]
        self.rssSave(directory, "rssyear.xml", "Bible in a year", year, year5)
        self.rssSave(directory, "rssday.xml", "Daily Bible Reading", day, day5)
        return

    def rssSave(self, directory, rssFile, title, source, filelist):
        filename = os.path.join(directory, rssFile)
        r1 = '''<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
   <title>'''
        r2 = '''</title>
   <link>''' + self.prefix + '''</link>
   <description>Latest set of readings</description>'''
        r3 = '''</channel>
</rss>
'''
        with open(filename, 'w', encoding="utf-8") as f:
            print(r1, file=f)
            print(title, file=f)
            print(r2, file=f)
            for name in filelist:
                date = parse(name.replace(".html", ""))
                pubDate = date.strftime("%a, %d %b %Y")
                print("   <item>", file=f)
                print("      <title>Reading for " +
                      pubDate + "</title>", file=f)
                print("      <link>" + self.prefix + source.replace(directory,
                                                                    "")[1:] + "/" + name + "</link>", file=f)
                print("      <description>Reading for " +
                      pubDate + "</description>", file=f)
                print("      <pubDate>" + pubDate + "</pubDate>", file=f)
                print("   </item>", file=f)
            print(r3, file=f)
        return


if __name__ == "__main__":
    tree = Moravian("https://www.moravian.org/the-daily-texts/", version="NLT")
    '''
   tree.show()
   tree.showDaily()
   print()
   tree.showWatchwords()
   print()
   tree.showOneYear()
   print()
   tree.saveDaily(directory="/var/www/html")
   tree.saveYear(directory="/var/www/html")
   '''
    tree.webSave(directory="/var/www/html")
