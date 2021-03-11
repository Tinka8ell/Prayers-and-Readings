# parse html
import urllib.request # as Request
# used to parse values into the url
import urllib.parse
import re, os
from pathlib import Path
from bs4 import BeautifulSoup
from dateutil.parser import parse
from datetime import date


class WebTree:
   def __init__(self, url, values=None):
      self.url = url
      self.directory = "/var/www/html"
      self.prefix = "http://piweb/"
      self.data = None
      self.values = values
      if values:
         data = urllib.parse.urlencode(values)
         self.data = data.encode('utf-8') # data should be bytes
      self.root = None
      self.root = self.read()
      self.parse()
      return

   def read(self):
      url = self.url
      data = self.data
      headers = {}
      headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
      req = urllib.request.Request(url, headers=headers, data=data)
      with urllib.request.urlopen(req) as f:
         g = f.read().decode('utf-8')
      # generate element tree
      root = BeautifulSoup(g, 'html.parser')
      return root

   def parse(self):
      return

   def show(self):
      print("url:", self.url)
      print("values:", self.values)
      return


if __name__ == "__main__":
   tree = WebTree("https://www.moravian.org/the-daily-texts/")
   tree.show()
