# parse html

from Moravian import Moravian
from BibleReading import BibleReading, cleanText, tagText
from DailyPrayer import DailyPrayer
from dateutil.parser import parse
from datetime import date, timedelta
import os
from pathlib import Path

class PrayerTemplate():
   def __init__(self, name, version="NIVUK"):  # default to English NIV
      self.version = version
      self.name = name
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
      self.northumbrian = "https://www.northumbriacommunity.org/offices/morning-prayer/"
      self.moravian = "https://www.moravian.org/the-daily-texts/"
      self.paras = []
      self.title = None
      self.addDate = False
      self.weekLink = None
      self.parse()
      return

   def parse(self):
      directory = os.path.dirname(__file__)
      parent = directory # keep finger on parent
      name = self.name
      filename = os.path.join(directory, name + ".txt")
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
               url = line[pos: ].strip()
               line = (tag, url)
            elif paraType == "I":
               self.addDate = True
            elif paraType == "D":
               self.addDate = True
            elif paraType == "T":
               self.title = line
            if paraType != "#": # ignore commencted lines
               self.paras.append((paraType, line))
            line = f.readline()
      return

   def closeTag(self, f):
      if self.closingTag != "":
         print(self.closingTag, file=f)
         self.closingTag = ""
      return

   def openTag(self, f, tag, para):
      # print("OpenTag:", tag, para, self.closingTag)
      isNotBr = True
      if tag == "br":
         if self.closingTag == "</p>":
            tag = "<br/>"
            isNotBr = False
         else:
            tag = "p"
      if isNotBr:
         self.closeTag(f)
         self.closingTag = "</" + tag + ">"
         tag = "<" + tag + ">"
      print(tag + cleanText(para).encode('ascii', 'xmlcharrefreplace').decode(), end='', file=f) # no newline
      # print("OpenTag -", tag, self.closingTag, isNotBr)
      return

   def html(self, directory=None):
      if not directory:
         # get the name of our directory
         directory = os.path.dirname(__file__)
      parent = directory # keep finger on parent
      directory = os.path.join(directory, "prayers")
      if not os.path.exists(directory):
         os.mkdir(directory)
      name = self.name
      if self.addDate:
         name += date.today().isoformat()
      filename = os.path.join(directory, name + ".html")
      # print("Creating prayer page:", filename)
      title = "Template for: " + date.today().strftime("%A %d %B %Y")
      if self.title:
         title = self.title
      with open(filename, 'w', encoding="utf-8") as f:
         print(self.p1, file=f)
         print(title, file=f)
         print(self.p2, file=f)
         print(tagText(title, "h1"), file=f)
         self.closingTag = ""
         for paraType, para in self.paras:
            if paraType == "B": # Bible passage
               self.closeTag(f)
               bible = BibleReading(para, self.version)
               bible.htmlParas(f, reading=True)
            elif paraType == "": # line break
               self.openTag(f, "br", para)
            elif paraType == "P": # paragraph
               self.openTag(f, "p", para)
            elif paraType == "U": # URL - link
               self.openTag(f, "p", '<a href="' + para[1] + '">' + para[0] + "</a>")
            elif paraType == "S": # strong - bold
               self.openTag(f, "p", "<b>" + para + "</b>")
            elif paraType == "H": # heading
               self.openTag(f, "h2", para)
            elif paraType == "D": # date
               dateFormat = "%A %d %B %Y"
               if para and para != "":
                  dateFormat = para
               self.openTag(f, "h2", date.today().strftime(dateFormat))
            elif paraType == "W": # link to previous and next week days
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
                  yesterday = (thisDay - day1).strftime(dateFormat)
                  tomorrow = (thisDay + day1).strftime(dateFormat)
                  self.weekLink = '<div class="left">'
                  self.weekLink += tagText('<<<<< ' + yesterday, 'a href="./' + yesterday + '.html"')
                  self.weekLink += '</div><br/><div class="right">'
                  self.weekLink += tagText(tomorrow + " >>>>>", 'a href="./' + tomorrow + '.html"')
                  self.weekLink += "</div>"
               self.openTag(f, "p", self.weekLink)
            elif paraType == "I": # Insert from another page
               self.closeTag(f)
               if para == "Moravian":
                  insert = Moravian(self.moravian, version=self.version)
                  # print("Moravian:", insert.show())
                  insert.html(f, showdivs=False)
               if para == "Northumbrian":
                  insert = DailyPrayer(self.northumbrian, version=self.version)
                  # print("DailyPrayer:", insert.show())
                  insert.html(f, showdivs=False)
         self.closeTag(f)
         print(self.p3, file=f)
      if os.name == 'posix':
         # point symbolic link to file created:
         symbolic = os.path.join(parent, self.name + ".html")
         filename = Path(filename)
         symbolic = Path(symbolic)
         if symbolic.exists():
            os.unlink(symbolic)
         os.symlink(filename, symbolic)
      return


if __name__ == "__main__":
   import sys
   argv = sys.argv
   # testing parameters:
   # argv = ["testing", "Wednesday", "Thursday", "Friday"]
   # argv = ["testing", "midday"]
   if len(argv) > 1:
      for name in argv[1:]:
         print("Processing:", name)
         if name.endswith(".txt"):
            name = name[0: -4]
            print("Processing:", name)
         if name not in ("Upload", "weekly", "Morning", "Evening") :
            prayer = PrayerTemplate(name, version="NLT")
            prayer.html(directory="/var/www/html")
         else:
            print("skipping", name)
            pass
   else:
      for name in ("Morning", "Evening") :
         # print("Processing:", name)
         prayer = PrayerTemplate(name, version="NLT")
         prayer.html(directory="/var/www/html")
