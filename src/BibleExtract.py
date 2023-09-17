# Process a bible reference as a passage
#
#     Initially reference is any reference, but might become:
#         Chapter, or
#         Book, ...
#
#     Look up a bible reference on Bible Gateway.
#
#     Default to anglicised NIV, but can be overridden with version.
#     Using WebTree read the page and extract the content as marked up text.
#     So skip titles, headings and chapter numbers.
#     Also skip footnotes and references.
#     Try to add as much relevant formatting and verse markers.

import os
import re

from WebTree import WebTree


def findbad(text, show=True):
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
    if show and not ok:
        print(text)
    return

def cleanText(text, xmlReplace=False):
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
    findbad(text)
    if xmlReplace:
        text = text.encode('ascii', 'xmlcharrefreplace').decode()
    return text


def tagText(text, tag):
    """
    Wrap an html tag arround some text.
    """
    html = ''
    if text:
        closeTag = "/" + tag.split(" ")[0]  # strip after first space
        if tag[-1] == "/":
            closeTag = None
        html = "<" + tag + ">" + \
            cleanText(text, xmlReplace=True)
        if closeTag:
            html += "<" + closeTag + ">"
    return html

def removeSection(passage, section, class_=None):
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

def flattenSection(passage, section, class_=None):
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

def isSpecial(name, nameTest, attributes, attributesTest):
    return name == nameTest and attributes.find(attributesTest) >= 0

def endIndent(isSpan, indent, html):
    if isSpan:
        html.append("</span>")
        isSpan = False
    if indent != "":
        html.append('</span>\n')
    indent = ""
    return (isSpan, indent)

def getIndentAndAddText(indent, html, key, text):
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


class BibleExtract(WebTree):
    """
    Initially reference is any reference, but might become:
        Chapter, or
        Book, ...

    Look up a bible reference on Bible Gateway.

    Default to anglicised NIV, but can be overridden with version.
    Using WebTree read the page and extract the content as marked up text.
    So skip titles, headings and chapter numbers.
    Also skip footnotes and references.
    Try to add as much relevant formatting and verse markers.
    """

    def __init__(self, reading, version="NIVUK"):  # default to English NIV
        self.version = version
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
        # skip to the "passage text" divisions in the tree -  this may be reduced to one!
        passages = self.root.findAll('div', class_="passage-text")
        
        # what if no passage found?
        for passage in passages:
            # print("passage:", passage.prettify()) # debug
            # remove footnote divisions
            removeSection(passage, "div", "footnotes")
            # remove crossref divisions
            removeSection(passage, "div", re.compile("crossrefs"))
            # remove publisher info divisions - this may be used to test for version changes!
            removeSection(passage, "div", re.compile("publisher"))
            # print("cleaned passage:", passage.prettify()) # debug
            removeSection(passage, "h3") # the added headings, but h4 used as extra info (not has headings)
            removeSection(passage, ["sup", "span"], ["chapternum", "footnote"])
            flattenSection(passage, "div", ["passage-text", "passage-content", "text-html"])
            flattenSection(passage, "span", ["text", "woj", "chapter-1", "indent-1-breaks"])#, "indent-1"])

            self.decompress(passage, "")
            self.generateVerses()

        return
    
    def decompress(self, passage, prefix, poetry=""):
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
            if isSpecial(passage.name, "sup", attributes, "class: versenum"):
                self.doSpecial(passage, "verse", prefix)
            elif isSpecial(passage.name, "span", attributes, "class: selah"):
                self.doSpecial(passage, "selah", prefix, poetry)
            elif isSpecial(passage.name, "span", attributes, "class: small-caps"):
                self.doSpecial(passage, "lord", prefix, poetry)
            elif isSpecial(passage.name, "i", attributes, ""):
                self.doSpecial(passage, "emphasis", prefix, poetry)
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
                    self.decompress(child, self.indent + prefix, nextPoetry)
        else:
            self.doSpecial(passage, "text", prefix, poetry)
        return
    
    def doSpecial(self, passage, tag, prefix="", poetry=""):
        text = ""
        for string in passage.stripped_strings:
            string = string.strip()
            text += " " + string
        text = cleanText(text)
        # if len(text) > 0:
        self.lines.append(prefix + "." + tag + poetry + ": " + text)

    def generateVerses(self):
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
                        (isSpan, indent) = endIndent(isSpan, indent, html)
                        self.verses[verseNumber] = html
                        (html, isHeading, isSpan) = ([], False, False)
                        # html = []
                        # isHeading = False
                        # isSpan = False
                    verseNumber = text
                case "h": # heading
                    (isSpan, indent) = endIndent(isSpan, indent, html)
                    html.append("</p>" + "\n")
                    html.append('<div class="heading">')
                    isHeading = True
                case "p": # paragraph
                    (isSpan, indent) = endIndent(isSpan, indent, html)
                    if isHeading:
                        html.append("</div>" + "\n")
                        isHeading = False
                    else:
                        html.append("</p>" + "\n")
                    html.append('<p>')
                case "l": # lord
                    lord = '<span class="lord">' + text + '</span>'
                    indent = getIndentAndAddText(indent, html, key, lord)
                case "s": # selah
                    selah = '<span class="selah">' + text + '</span>'
                    indent = getIndentAndAddText(indent, html, key, selah)
                case "e": # emphasis
                    emphasis = '<span class="emphasis">' + text + '</span>'
                    indent = getIndentAndAddText(indent, html, key, emphasis)
                case "t": # text
                    indent = getIndentAndAddText(indent, html, key, text)
        endIndent(isSpan, indent, html)
        self.verses[verseNumber] = html
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
        for para in self.lines:
            print(">>>", para)
        print("reading:", self.reading)
        return

    def htmlParas(self, f, reading=False):
        """
        Format the paragraphs as html and send to given output file f.

        Wrap the paragraphs in a "div" of class "bible".
            Wrap each paragraph in a "p".
            If reading is requested:
            Wrap it in a "p" of class "reading".
        """
        html = self.getHtmlParas(reading)
        print(html, file=f)
        return

    def getHtmlParas(self, reading=False):
        """
        Format the paragraphs as html.

        Wrap the paragraphs in a "div" of class "bible".
            Wrap each paragraph in a "p".
            If reading is requested:
            Wrap it in a "p" of class "reading".
        """
        html = []
        html.append('<div class="bible">')
        for para in self.lines:
            html.append(tagText(para, "p"))
        if reading:
            html.append(tagText(self.reading, 'p class="reading"'))
        html.append('</div>')
        return '\n'.join(html)


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
    # findbad("“’”")
    # findbad("Let him kiss me with the kisses of his mouth&nbsp;–")
    def testIt(book, chapter, version):
        reference = book + " " + str(chapter)
        print("BibleExtract(\"" + reference + "\", version=\"" + version + "\")")
        bible = BibleExtract(reference, version=version)
        bible.show()
        
    # testIt("john", 1, "NLT")
    # testIt("psalm", 3, "NLT")
    # testIt("psalm", 3, "NIVUK")
    # testIt("john", 3, "MSG")
    # testIt("john", 3, "NLT")
    # testIt("phil", 2, "NIVUK")
    testIt("song", 1, "NLT")
    testIt("song", 1, "NIVUK")
    
