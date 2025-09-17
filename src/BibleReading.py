# Process a bible passage
#
#     Look up a bible reading on Bible Gateway.
#
#     Default to anglicised NIV, but can be overridden with version.
#     Using WebTree read the page and extract the text only
#     to internal list of paragraphs.
#     So skip titles, headings, verse and chapter numbers.
#     Show the paragraphs as html.

import os
import re

from WebTree import WebTree


def cleanText(text, xmlReplace=False):
    """
    Utility to clean up text that may be in a web page.

    Basically remove non-ascii punctuation.
    Also remove excessive white space characters.
    """
    if text:
        swaps = {"â€™": "'",  # remove funny apostrophes
                 "â€˜": "'",  # remove funny apostrophes
                 "â€œ": '"',  # remove funny double-quotes
                 "â€�": '"',  # remove funny double-quotes
                 "â€”": " - ",  # remove funny dashes
                 "â€¦": "...",  # remove funny ellipses
                 "\n": " ",  # remove excess new-lines
                 "  ": " "}  # remove excess spaces
        for key in swaps.keys():
            text = text.replace(key, swaps[key])
        # join up random gaps in punctuation
        text = re.sub(r"(\w)\s+([!\");:'.,?])", r"\1\2", text)
    else:
        text = ''
    text = text.strip()
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

def removeSection(passage, section, class_):
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


class BibleReading(WebTree):
    """
    Look up a bible reading on Bible Gateway.

    Default to anglicised NIV, but can be overridden with version.
    Using WebTree read the page and extract the text only
    to internal list of paragraphs.
    So skip titles, headings, verse and chapter numbers.
    Show the paragraphs as html.
    """

    def __init__(self, reading, version="NIVUK"):  # default to English NIV
        self.version = version
        self.reading = reading
        url = "https://www.biblegateway.com/passage/"
        values = {"search": reading, "version": version}
        super().__init__(url, values=values)
        return

    def parse(self):
        """
        Overrides the parent class (do nothing) and extracts
        all the text less the chapter, verse numbers and any
        headings and titles.
        Create a list of paragraphs and store in self.paras.
        """
        if self.root == None:
            raise Exception("*** Error getting web page for " + self.reading + " ***")
        paras = []
        # skip to the "passage text" divisions in the tree
        passages = self.root.findAll('div', class_="passage-text")
        # what if no passage found?
        for passage in passages:
            # print("passage:", passage.prettify()) # debug
            # remove footnote divisions
            removeSection(passage, "div", "footnotes")
            # remove crossref divisions
            removeSection(passage, "div", re.compile("crossrefs"))
            # remove publisher info divisions
            removeSection(passage, "div", re.compile("publisher"))
            # print("cleaned passage:", passage.prettify()) # debug
            ps = passage.find_all("p")
            for nextP in ps:
                # remove verse numbers, chapter numbers and footnotes
                removeSection(nextP,
                              ["sup", "span"],
                              ["versenum", "chapternum", "footnote"])
                # ## print("nextP:", nextP.prettify()) # debug
                text = ""
                # compile paragraph
                for string in nextP.stripped_strings:
                    string = string.strip()
                    text += " " + string
                text = text.strip()
                # why am I removing trailing quotes?
                while text[-1] == "'" or text[-1] == '"':
                    text = text[:-1]
                while text[0] == "'" or text[0] == '"':
                    text = text[1:]
                paras.append(cleanText(text))
        self.paras = paras
        return

    def show(self):
        """
        Extended display function for debugging.
        """
        super().show()
        print("reading:", self.reading)
        print("version:", self.version)
        print("paras:", len(self.paras))
        for para in self.paras:
            print("   " + para)
        return

    def showPassage(self):
        """
        Display passage for debugging.
        """
        for para in self.paras:
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
        for para in self.paras:
            html.append(tagText(para, "p"))
        if reading:
            html.append(tagText(self.reading, 'p class="reading"'))
        html.append('</div>')
        return '\n'.join(html)


if __name__ == "__main__":
    """
    Test code while debugging.
    """
    r'''
    text = "Sovereign Lord , for the awesome day of the Lord 's judgment is near. The"
    print(text, re.sub(r'(\w)\s+([!\"()\-\;:\'\.,\?])', r"\1\2", text))  # type: ignore
    text = 'Then he said, "Anyone with ears to hear should listen and understand."'
    print(text, re.sub(r"(\w)\s+([!\"()-;:'.,?])", r"\1\2", text))
    '''
    '''
    bible = BibleReading("Psalm 147:2â€“3", version="NLT")
    bible.showPassage()
    print()
    bible.htmlParas(None)
    print()
    bible.show()
    '''
    for i in range(1, 9):
        bible = BibleReading("song " + str(i), version="NLT")
        print(bible.getHtmlParas(reading=True))
