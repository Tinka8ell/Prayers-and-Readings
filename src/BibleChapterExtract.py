# Process a chapter of a book of a bible version
#
#     Requires: 
#         Version abrieviation
#         Book abrieviation (can be full name)
#             Optional book number and space
#             At least fist 3 characters of name
#         Chapter number
#
#     Look up a bible reference on Bible Gateway.
#
#     Default to anglicised NIV(UK), but can be overridden with version.
#     Using WebTree read the page and extract the content as marked up text.
#     So skip titles, headings and chapter numbers.
#     Also skip footnotes and references.
#     Try to add as much relevant formatting and verse markers.
#     Add all verses (if not already in the Bible Store)
#     Identify the next and previous chapters that need to be processed

import os
import re

from WebTree import WebTree
from BibleStore import *


def _findbad(text, isDebug=False):
    ok = True
    for ch in text:
        if not ch.isascii():
            ok = False
            # string with encoding 'utf-8'
            arr = bytes(ch, 'utf-8')
            # arr2 = bytes(ch, 'ascii')
            ascii = ""
            pref = " - "
            for byte in arr:
                ascii += pref + str(byte)
                pref = ", "
            # pref = " - "
            # for byte in arr2:
            #     ascii += pref + str(byte)
            #     pref = ", "
            print(ascii)
    if isDebug and not ok:
        print(text)
    return

def _cleanText(text, xmlReplace=False):
    """
    Utility to clean up text that may be in a web page.

    Basically remove non-ascii punctuation.
    Also remove excessive white space characters.
    """
    if text:
        swaps = { 
            bytes([226, 128, 152]).decode('utf-8'): "'",  # remove funny apostrophes
            bytes([226, 128, 153]).decode('utf-8'): "'",  # remove funny apostrophes
            bytes([226, 128, 148]).decode('utf-8'): " - ",  # remove funny apostrophes
            bytes([226, 128, 156]).decode('utf-8'): '"',  # remove funny double-quotes
            bytes([226, 128, 157]).decode('utf-8'): '"',  # remove funny double-quotes
            bytes([194, 160]).decode('utf-8'): "&nbsp;",  # remove funny non-breaking space
            bytes([226, 128, 147]).decode('utf-8'): "-",  # remove funny dashes
            bytes([226, 128, 148]).decode('utf-8'): " - ",  # remove funny dashes
            bytes([194, 174]).decode('utf-8'): " (R) ",  # replace registered symbol
            bytes([194, 169]).decode('utf-8'): " (C) ",  # replace copyright symbol
        #  bytes().decode('utf-8'): "...",  # remove funny ellipses
            "\n": " ",  # remove excess new-lines
            "  ": " ",  # remove excess spaces
        }
        for key in swaps.keys():
            text = text.replace(key, swaps[key])
        # join up random gaps in punctuation - not sure about this and quotes ...
        # text = re.sub(r"(\w)\s+([!\");:'.,?])", r"\1\2", text)
    else:
        text = ''
    text = text.strip()
    _findbad(text)
    if xmlReplace:
        text = text.encode('ascii', 'xmlcharrefreplace').decode()
    return text

def _removeSection(passage, section, class_=None):
    """
    Remove all sections with given class from the passage.
    Passage is a BeautifulSoup sub-tree.
    Section is html tag or list of tags.
    Class is a class name, regular expression, or list of class names.
    """
    div = passage.find(section, class_=class_)
    # remove matching sections
    while div:
        div.decompose()  # remove it
        div = passage.find(section, class_=class_)
    return

def _flattenSection(passage, section, class_=None):
    """
    Replace all sections with given class with their children the passage.
    Passage is a BeautifulSoup sub-tree.
    Section is html tag or list of tags.
    Class is a class name, regular expression, or list of class names.
    """
    div = passage.find(section, class_=class_)
    # remove matching sections
    while div:
        div.replaceWithChildren() # remove this wrapper
        div = passage.find(section, class_=class_)
    return

def _isSpecial(name, nameTest, attributes, attributesTest):
    return name == nameTest and attributes.find(attributesTest) >= 0

def _endIndent(isSpan, indent, html):
    if isSpan:
        html.append("</span>")
        isSpan = False
    if indent != "":
        html.append('</span>\n')
    indent = ""
    return (isSpan, indent)

def _getIndentAndAddText(indent, html, key, text):
    nextIndent = key[-1]
    if not nextIndent.isdecimal():
        nextIndent = ""
    if indent != nextIndent:
        if indent != "":
            html.append('</span>\n')
        indent = nextIndent
        html.append('<span class="indent-' + indent + '">')
    appendText = text
    if len(appendText) > 0 and appendText[0].isalpha():
        appendText = " " + appendText
    if key[0] == "t" and len(appendText) > 0: # and not appendText[-1].isalpha():
        appendText += " "
    html.append(appendText)
    return indent


class BibleChapterExtract(WebTree):
    """
    Process a chapter of a book of a bible version

        Requires: 
            Version abrieviation
            Book abrieviation (can be full name)
                Optional book number and space
                At least fist 3 characters of name
            Chapter number
        Look up a bible reference on Bible Gateway.

        Default to anglicised NIV(UK), but can be overridden with version.
        Using WebTree read the page and extract the content as marked up text.
        So skip titles, headings and chapter numbers.
        Also skip footnotes and references.
        Try to add as much relevant formatting and verse markers.
        Add all verses (if not already in the Bible Store)
        Identify the next and previous chapters that need to be processed
    """

    def __init__(self, book, chapter, version="NIVUK"):  # default to English NIV
        self.version = version
        self.versionName = "Was not set"
        self.book = book
        self.chapter = chapter
        reading = book + " " + str(chapter)
        self.reading = reading
        self.lines = []
        self.verses = dict()
        self.indent = ""
        url = "https://www.biblegateway.com/passage/"
        values = {"search": reading, "version": version}
        super().__init__(url, values=values)
        return

    def parse(self):
        """
        Overrides the parent class (do nothing) and does the work!
        """
        self.processPreviousNext()
        self.processPublishers()
        # skip to the "passage text" divisions in the tree -  this may be reduced to one!
        passages = self.root.findAll('div', class_="passage-text")
        # print("Found", len(passages), "passages, processing each ...")
        # what if no passage found?
        for passage in passages:
            self._processPassage(passage)
        return
    
    def _processPassage(self, passage):
        # print("passage:", passage.prettify()) # debug
        # remove footnote divisions
        _removeSection(passage, "div", "footnotes")
        # remove crossref divisions
        _removeSection(passage, "div", re.compile("crossrefs"))
        # remove publisher info divisions - this may be used to test for version changes!
        # self.processPublishers(passage)
        # Publisher info is not in passage sections, so not required here ...
        _removeSection(passage, "div", re.compile("publisher"))
        # print("cleaned passage:", passage.prettify()) # debug
        _removeSection(passage, "h3") # the added headings, but h4 used as extra info (not has headings)
        _removeSection(passage, ["sup", "span"], ["chapternum", "footnote"])
        _flattenSection(passage, "div", ["passage-text", "passage-content", "text-html"])
        _flattenSection(passage, "span", ["text", "woj", "chapter-1", "indent-1-breaks"])#, "indent-1"])

        self._decompress(passage, "")
        self._generateVerses()
        return
    
    def processPreviousNext(self, isDebug=False):
        """
        Get previous and next chapter names if exist
        """
        self.nextChapter = None
        self.prevChapter = None
        pages = self.root.findAll("div",  class_="prev-next")
        for page in pages:
            links = page.findAll("a", class_="next-chapter")
            for link in links:
                self.nextChapter = link.attrs["title"]
                if isDebug:
                    print("Next chapter:", self.nextChapter)
            links = page.findAll("a", class_="prev-chapter")
            for link in links:
                self.prevChapter = link.attrs["title"]
                if isDebug:
                    print("Prev chapter:", self.prevChapter)
        return
    
    def processPublishers(self, isDebug=False):
        publishers = self.root.findAll("div", re.compile("publisher"))
        for publisher in publishers:
            for child in publisher.children:
                match child.name:
                    case "strong":
                        _flattenSection(child, "a")
                        self.versionName = _cleanText(" ".join(child.stripped_strings))
                        if isDebug:
                            print("   Version:", self.versionName)
                    case "p":
                        _flattenSection(child, "a")
                        self.copyright = _cleanText(" ".join(child.stripped_strings))
                        years = re.findall("\\D\\d\\d\\d\\d\\D", self.copyright)
                        self.year = int(years[-1][1:5])
                        if isDebug:
                            print("   Copyright:", self.year, " - ", self.copyright)
        return
    
    def _decompress(self, passage, prefix, poetry=""):
        if passage.name:
            attributes =  ""
            nextPoetry = poetry
            if passage.name != "p" and passage.name != "h4" and passage.attrs:
                for attr in passage.attrs.keys():
                    value = passage.attrs[attr]
                    if isinstance(value, (list, tuple)):
                        value = ", ".join(passage.attrs[attr])
                    attributes += ", " + attr + ": " + value
                if len(attributes) > 1:
                    attributes = attributes[1:] # remove the leading ','
            if _isSpecial(passage.name, "sup", attributes, "class: versenum"):
                self._doSpecial(passage, "verse", prefix)
            elif _isSpecial(passage.name, "span", attributes, "class: selah"):
                self._doSpecial(passage, "selah", prefix, poetry)
            elif _isSpecial(passage.name, "span", attributes, "class: small-caps"):
                self._doSpecial(passage, "lord", prefix, poetry)
            elif _isSpecial(passage.name, "i", attributes, ""):
                self._doSpecial(passage, "emphasis", prefix, poetry)
            else:
                children = passage.children
                if attributes.find("poetry") >= 0:
                    nextPoetry = "1"
                elif attributes.find("indent-1") >= 0: # very common
                    nextPoetry = "2"
                elif attributes.find("indent-2") >= 0: # have seen this
                    nextPoetry = "3"
                elif attributes.find("indent-3") >= 0: # probably overkill!
                    nextPoetry = "4"
                else:
                    self.lines.append(prefix + "." + passage.name + attributes)
                for child in children:
                    self._decompress(child, self.indent + prefix, nextPoetry)
        else:
            self._doSpecial(passage, "text", prefix, poetry)
        return
    
    def _doSpecial(self, passage, tag, prefix="", poetry=""):
        text = ""
        for string in passage.stripped_strings:
            string = string.strip()
            text += " " + string
        text = _cleanText(text)
        # if len(text) > 0:
        self.lines.append(prefix + "." + tag + poetry + ": " + text)

    def _generateVerses(self):
        verseNumber = ""
        (html, isHeading, isSpan) = ([], False, False)
        indent = ""
        for line in self.lines:
            parts = line.split(": ", 1)
            key = parts[0][1:]
            text = ""
            if len(parts) > 1:
                text = parts[1]
            keyType = key[0]
            match keyType:
                case "v": # verse indicator
                    # if verseNumber == "" not yet started a verse
                    # but if text (next verse number) 2 or more, we've skipped verse 1
                    # so need to create it
                    if verseNumber == "" and text.startswith("2"):
                        verseNumber = "1"
                    if verseNumber != "":
                        (isSpan, indent) = _endIndent(isSpan, indent, html)
                        self._saveVerse(verseNumber, html)
                        (html, isHeading, isSpan) = ([], False, False)
                        # html = []
                        # isHeading = False
                        # isSpan = False
                    verseNumber = text
                case "h": # heading
                    (isSpan, indent) = _endIndent(isSpan, indent, html)
                    html.append("</p>" + "\n")
                    html.append('<div class="heading">')
                    isHeading = True
                case "p": # paragraph
                    (isSpan, indent) = _endIndent(isSpan, indent, html)
                    if isHeading:
                        html.append("</div>" + "\n")
                        isHeading = False
                    else:
                        html.append("</p>" + "\n")
                    html.append('<p>')
                case "l": # lord
                    lord = '<span class="lord">' + text + '</span>'
                    indent = _getIndentAndAddText(indent, html, key, lord)
                case "s": # selah
                    selah = '<span class="selah">' + text + '</span>'
                    indent = _getIndentAndAddText(indent, html, key, selah)
                case "e": # emphasis
                    emphasis = '<span class="emphasis">' + text + '</span>'
                    indent = _getIndentAndAddText(indent, html, key, emphasis)
                case "t": # text
                    indent = _getIndentAndAddText(indent, html, key, text)
        _endIndent(isSpan, indent, html)
        self._saveVerse(verseNumber, html)
        return
    
    @db_session
    def _saveVerse(self, verseNumber, html, isDebug=False):
        self.verses[verseNumber] = html
        numbers = verseNumber.split("-")
        firstNumber = int(numbers[0])
        lastNumber = None
        if len(numbers) > 1:
            lastNumber = int(numbers[1])
        versions = select(v for v in Version if v.Abbreviation == self.version)[:]
        if len(versions) > 0:
            version = versions[0]
            version.Name = self.versionName
            version.Year = self.year
            version.Copyright = self.copyright
        else:
            if isDebug:
                print("Creating Version:", self.version)
            version = Version(Abbreviation = self.version, Name = self.versionName, Year = self.year, Copyright = self.copyright)

        extenedAbbreviation = self.book[0:3]
        books = select(b for b in Book if b.ExtenedAbbreviation == extenedAbbreviation and b.version == version)[:]
        if len(books) > 0:
            book = books[0]
        else:
            if isDebug:
                print("Creating Book:", self.book)
            book = Book(ExtenedAbbreviation = extenedAbbreviation, Name = self.book, Total = 0, version = version)

        chapters = select(c for c in Chapter if c.Number == self.chapter and c.book == book)[:]
        if len(chapters) > 0:
            chapter = chapters[0]
        else:
            if isDebug:
                print("Creating Chapter:", self.chapter)
            chapter = Chapter(Number = self.chapter, Verses = 0, book = book)
        if book.Total < self.chapter:
            if isDebug:
                print("Updating Book:", self.book, " to total verses ", self.chapter)
            book.Total = self.chapter
        
        content = "\n".join(html)
        if isDebug:
            print("Creating Verse:", verseNumber)
        verses = select(v for v in Verse if v.Number == firstNumber and v.Last == lastNumber and v.chapter == chapter)[:]
        if len(verses) > 0: # re-use old record
            verse = verses[0]
            verse.Content = content
        else: # create new record
            verse = Verse(Number = firstNumber, Last = lastNumber, Content = content, chapter = chapter)
        if not lastNumber:
            lastNumber = firstNumber
        if chapter.Verses < lastNumber:
            if isDebug:
                print("Updating Chapter:", self.chapter, " to total verses ", lastNumber)
            chapter.Verses = lastNumber

        for verseNumber in range (firstNumber, lastNumber + 1):
            if isDebug:
                print("Creating Lookup for Verse:", verseNumber)
            lookups = select(l for l in Lookup if l.Number == verseNumber and l.chapter == chapter)[:]
            if len(lookups) > 0: # re-use old record
                lookup = lookups[0]
                lookup.verse = verse
            else: # create new record
                lookup = Lookup(Number = verseNumber, chapter = chapter, verse = verse)
        return
    
    def show(self):
        """
        Extended display function for debugging.
        """
        super().show()
        print("Reading:", self.reading)
        print("Version:", self.version)
        # print("Paras:", len(self.lines))
        # for para in self.lines:
        #     print("   " + para)
        # print("Verses:", len(self.verses))
        # for verseNumber in self.verses.keys():
        #     print("Verse " + verseNumber + ":")
        #     print("".join(self.verses[verseNumber]))
        print("\n" + self.getPassage(1, 3))
        print("\n" + self.getPassage(4, 6))
        return

    def getPassage(self, first, last):
        passage = ""
        for verse in range(first, last + 1):
            passage += "".join(self.verses[str(verse)])
        if passage[0:4] == "</p>":
            passage = passage[4:]
        else:
            passage = "<p>" + passage
        if passage[-3:] == "<p>":
            passage = passage[:-4]
        else:
            passage += "</p>"
        return "<h1> Verses " + str(first) + " to " + str(last) + " </h1>\n" + passage

    def showPassage(self):
        """
        Display passage for debugging.
        """
        for line in self.lines:
            print(">>>", line)
        print("reading:", self.reading)
        return


if __name__ == "__main__":
    """
    Test code while debugging.
    """
    '''
    text = "Sovereign Lord , for the awesome day of the Lord 's judgment is near. The"
    print(text, re.sub(r"(\w)\s+([!\"()-;:'.,?])", r"\1\2", text))
    text = 'Then he said, "Anyone with ears to hear should listen and understand."'
    print(text, re.sub(r"(\w)\s+([!\"()-;:'.,?])", r"\1\2", text))
    '''
    '''
    bible = BibleExtract("Psalm 147:2â€“3", version="NLT")
    bible.showPassage()
    print()
    bible.htmlParas(None)
    print()
    bible.show()
    '''
    # _findbad("“’”")
    # _findbad("Let him kiss me with the kisses of his mouth&nbsp;–")
    def testIt(book, chapter, version):
        reference = book + " " + str(chapter)
        print("BibleExtract(\"" + reference + "\", version=\"" + version + "\")")
        bible = BibleChapterExtract(book, chapter, version=version)
        print("Version:", bible.year, bible.versionName, bible.copyright)
        print("Next:", bible.nextChapter)
        print("Previous:", bible.prevChapter)
        # bible.show()
        
    # testIt("john", 1, "NLT")
    # testIt("psalm", 3, "NLT")
    # testIt("psalm", 3, "NIVUK")
    testIt("john", 3, "MSG")
    # testIt("john", 3, "NLT")
    # testIt("john", 3, "NIVUK")
    # testIt("phil", 2, "NIVUK")
    # testIt("song", 1, "NLT")
    # testIt("song", 1, "NIVUK")
    testIt("gen", 1, "NIVUK")
    testIt("2 Chr", 1, "NLT")
