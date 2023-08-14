# parse html
#     Read a requested web page into a "tree" and parse it.
#     
#     Requires a url and will take an optional dictionary of values 
#     to be sent as parameters on the HTTP GET. 

from datetime import date
import os
from pathlib import Path
import re
import urllib.parse
import urllib.request  # as Request

from bs4 import BeautifulSoup # used to parse values into the url
from dateutil.parser import parse


class WebTree:
    """
    Read a requested web page into a "tree" and parse it.
    
    Requires a url and will take an optional dictionary of values 
    to be sent as parameters on the HTTP GET. 
    """

    def __init__(self, url, values=None):
        # unknown if this is used or not or even why it is here ...
        self.directory = "/var/www/html"
        self.prefix = "http://piweb/"
        # known code ...
        self.url = url
        self.values = values
        self.data = None
        if values:
            data = urllib.parse.urlencode(values)
            self.data = data.encode('utf-8')  # data should be bytes
        self.root = None
        self.root = self.read() # root of the tree
        self.parse() # use the overrideable parse() method to process it. 
        return

    def read(self):
        url = self.url
        data = self.data # could be None if no headers passed
        # create a bunch of headers so we don't look too robot like
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " 
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/79.0.3945.88 "
        "Safari/537.36"
        req = urllib.request.Request(url, headers=headers, data=data)
        with urllib.request.urlopen(req) as f:
            g = f.read().decode('utf-8')
        # generate element tree
        root = BeautifulSoup(g, 'html.parser')
        print("***** Pretty *****\n", root.prettify())
        return root

    def parse(self):
        """ 
        Default is to do nothing, but should be overridden by subclasses.
        """
        return

    def show(self):
        """
        Basic display function for debugging.
        """
        print("url:", self.url)
        print("values:", self.values)
        return


if __name__ == "__main__":
    # simple test of a known source page
    tree = WebTree("https://www.moravian.org/the-daily-texts/")
    tree.show()
