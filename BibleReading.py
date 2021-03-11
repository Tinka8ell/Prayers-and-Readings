# Process a bible passage
'''
import urllib.request # as Request
# used to parse values into the url
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup
from dateutil.parser import parse
from datetime import date
'''
from WebTree import WebTree
import re, os

def cleanText(text):
   if text:
      swaps = {"’": "'",   # remove funny apostrophes
               "‘": "'",   # remove funny apostrophes
               "“": '"',   # remove funny double-quotes
               "”": '"',   # remove funny double-quotes
               "—": " - ", # remove funny dashes
               "…": "...", # remove funny ellipses
               "\n": " ",  # remove excess new-lines
               "  ": " "}  # remove excess spaces
      for key in swaps.keys():
         text = text.replace(key, swaps[key])
      # join up randum gaps in puncturation 
      text = re.sub(r"(\w)\s+([!\");:'.,?])", r"\1\2", text)
   else:
      text = ''
   return text.strip()

def tagText(text, tag):
   html = ''
   if text:
      closeTag = "/" + tag.split(" ")[0] # strip after first space
      if tag[-1] == "/":
         closeTag = None
      html = "<" + tag + ">" + cleanText(text).encode('ascii', 'xmlcharrefreplace').decode()
      if closeTag:
         html += "<" + closeTag + ">"
   return html

class BibleReading(WebTree):
   def __init__(self, reading, version="NIVUK"):  # default to English NIV
      self.version = version
      self.reading = reading
      url = "https://www.biblegateway.com/passage/"
      values = {"search" : reading, "version" : version}
      super().__init__(url, values=values)
      return

   def parse(self):
      paras = []
      passages = self.root.findAll('div', class_="passage-text")
      for passage in passages:
         # what if no passage found?
         # print("passage:", passage.prettify()) # debug
         div = passage.find("div", class_="footnotes")
         # remove footnotes
         while div:
               div.decompose() # remove it
               div = passage.find("div", class_="footnotes")
         # remove crossrefs
         div = passage.find("div", class_=re.compile("crossrefs"))
         while div:
               div.decompose() # remove it
               div = passage.find("div", class_=re.compile("crossrefs"))
         # remove publisher info
         div = passage.find("div", class_=re.compile("publisher"))
         while div:
               div.decompose() # remove it
               div = passage.find("div", class_=re.compile("publisher"))
         # print("cleaned passage:", passage.prettify()) # debug
         ps = passage.find_all("p")
         for nextP in ps:
            # remove verse numbers, chapter numbers and footnotes
            verse = nextP.find(["sup", "span"], class_=["versenum", "chapternum", "footnote"])
            while verse:
               verse.decompose() # remove it
               verse = nextP.find(["sup", "span"], class_=["versenum", "chapternum", "footnote"])
            ### print("nextP:", nextP.prettify()) # debug
            text = ""
            # compile paragraph
            for string in nextP.stripped_strings:
               string = string.strip()
               '''
               if string[0].isalnum():
                  text += " " + string
               else:
                  text += string
               '''
               text += " " + string
            text = text.strip()
            while text[-1] == "'" or text[-1] == '"':
               text = text[:-1]
            while text[0] == "'" or text[0] == '"':
               text = text[1:]
            paras.append(cleanText(text))
      self.paras = paras
      return

   def show(self):
      super().show()
      print("reading:", self.reading)
      print("version:", self.version)
      print("paras:", len(self.paras))
      for para in self.paras:
         print("   " + para)
      return

   def showPassage(self):
      for para in self.paras:
         print(">>>", para)
      print("reading:", self.reading)
      return

   def htmlParas(self, f, reading=False):
      print('<div class="bible">', file=f)
      for para in self.paras:
         print(tagText(para, "p"), file=f)
      if reading:
         print(tagText(self.reading, 'p class="reading"'), file=f)
      print('</div>', file=f)
      return

   
if __name__ == "__main__":
   '''
   text = "Sovereign Lord , for the awesome day of the Lord 's judgment is near. The"
   print(text, re.sub(r"(\w)\s+([!\"()-;:'.,?])", r"\1\2", text))
   text = 'Then he said, "Anyone with ears to hear should listen and understand."'
   print(text, re.sub(r"(\w)\s+([!\"()-;:'.,?])", r"\1\2", text))
   '''
   '''
   bible = BibleReading("Psalm 147:2–3", version="NLT")
   bible.showPassage()
   print()
   bible.htmlParas(None)
   print()
   bible.show()
   '''
   for i in range(1,9):
      bible = BibleReading("song " + str(i), version="NLT")
      bible.htmlParas(None, reading=True)
   
