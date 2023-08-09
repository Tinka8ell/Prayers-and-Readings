# parse html

from datetime import date, datetime
import os

from bs4 import NavigableString

from WebTree import WebTree

from urllib.parse import urlparse

from csv import DictReader

from BibleReading import tagText, removeSection


def isStrong(nextP):
    return nextP.name == "strong" or nextP.name == "b"


class WorldWatchListTree(WebTree):
    """
    Build a list of countries from the World Watch List
    """

    def __init__(self, url):  # default to English NIV
        parts = urlparse(url)
        # scheme://netloc/path;parameters?query#fragment
        self.base = parts.scheme + "://" + parts.netloc
        super().__init__(url)
        return

    def parse(self):
        '''
        Find the wwl__rankings widget and get all it's li elements.
        Each of these contains an anchor element.
        The anchor element has a href attribute giving a url,
        and the text in the element is the country.
        Build a list of country, url pairs.
        '''
        # assuming they stay consistent and we can access from:
        #    https://www.opendoorsuk.org/persecution/world-watch-list/
        rankingsWidget = self.root.find('div', class_="wwl__rankings")
        ### print(rankingsWidget.prettify()) # debug
        listItems = rankingsWidget.find_all('li')
        self.worldWatchList = []
        for li in listItems:
            a = li.find('a')
            url = a['href']
            if url.startswith("/"):
                url = self.base + url
            text = ' '.join(a.stripped_strings)
            self.worldWatchList.append((text, url))
        ''' debug
        rank = 0
        for (country, url) in self.worldWatchList:
            rank += 1
            print(rank, country, url) # debug
        '''
        return

    def getList(self):
        return self.worldWatchList


class WorldWatchList():

    def __init__(self, url):
        self.url = url
        self.date = date.today()
        filename = "WorldWatchList.csv"
        refresh = True
        self.worldWatchList = []
        if os.path.exists(filename):
            listDate = datetime.fromtimestamp(os.path.getmtime(filename)).date()
            if listDate >= self.date:
                refresh = False
        ### print("Refresh =", refresh)
        if refresh:
            worldWatchListTree = WorldWatchListTree(url)
            self.worldWatchList = worldWatchListTree.getList()
            # save list for next time
            with open(filename, 'w') as f:
                print("rank,country,url", file=f)
                rank = 0
                for (country, url) in self.worldWatchList:
                    rank += 1
                    print(f"{rank},{country},{url}", file=f)
                f.close()
        else:
            # save list for next time
            with open(filename) as f:
                csv_reader = DictReader(f, )
                for row in csv_reader:
                    ### print("row:", row)
                    self.worldWatchList.append((row['country'], row['url']))
        ### print("Length =", len(self.worldWatchList))
        return

    def getToday(self):
        newYear = date(self.date.year, 1, 1).toordinal()
        dayNumber = self.date.toordinal() - newYear # get ordinal as zero based
        ### print("Date:", self.date, "number:", dayNumber)
        dayNumber %= len(self.worldWatchList) # index into world watch list
        ### print("Number:", dayNumber)
        country, url = self.worldWatchList[dayNumber]
        ### print("Today is day", dayNumber+1, "so country =", country, 'and url =', url)
        return country, url


class OpenDoors(WebTree):
    """
    Find today's country and prayer.
    """

    def __init__(self, url):  # default to English NIV
        # get the current list using url if necessary
        worldWatchList = WorldWatchList(url)
        self.date = worldWatchList.date
        # select today's country
        self.country, url = worldWatchList.getToday()
        super().__init__(url)
        return

    def parse(self):
        '''
        Find the prayer for today's country.
        '''
        # assuming they stay consistent and we can access from:
        #    https://www.opendoorsuk.org/persecution/world-watch-list/
        countryFeatureBoxWidget = self.root.find('div', class_="wwl-country__feature-box")
        ### print(countryFeatureBoxWidget.prettify()) # debug
        self.content = []
        removeSection(countryFeatureBoxWidget, "div", "small-label")
        for section in countryFeatureBoxWidget.find_all():
            text = ' '.join(section.stripped_strings)
            self.content.append(text)
        return

    def getDate(self):
        return self.date

    def getHtml(self, showdivs=True):
        html = []
        html.append(tagText("Open Doors World Watch List", "h2"))
        header = '<a href="' + self.url + '">Pray for ' + self.country + '</a>'
        html.append(tagText(header, "h3"))
        for line in self.content:
            html.append(tagText(line, tag="p"))
        return '\n'.join(html)


if __name__ == "__main__":
    insert = OpenDoors("https://www.opendoorsuk.org/persecution/world-watch-list/")
    print(insert.getHtml())

