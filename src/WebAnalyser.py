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
import json
from bs4 import Tag

from WebTree import WebTree


class WebAnalyser(WebTree):
    """
    Analyse a web page
    """

    def __init__(self, url, values=None, output=None, commands=None):
        super().__init__(url, values=values, output=output)
        self.commands = {}
        if commands:
            with open(commands, 'r', encoding = 'utf-8') as fp:
                self.commands = json.load(fp)
        return

    def parse(self):
        """
        Overrides the parent class (do nothing) and analyses what's there.
        Create a list of tags.

        Assumes commands is a file containing json:
        {
            filter: Key,
            skip: [Key],
            ignore: [Key],
            converty: [
                {
                    fromKey: Key,
                    toKey: Key,
                },
            ],
            extract: {
                key: Key,
                data: Key,
            }
        }
        where Key:
        {
            tag: String,
            attributes: [
                key: String,
                value: String,
            ]
        }
        where value is either specific string (output) or matching string (input, can and often withh be specific)
        and all attributes declared must match, but other attributes can be present and are not tested.
        """
        content = self.filterContent(self.root, self.commands.filter)
        content = self.processContent(content)
        self.tags = self.extractContent(content)
        return
    
    def filterContent(self, root, filter):
        everything = root
        if (filter):
            if filter.tag:
                attrs = {}
                if filter.attributes:
                    for atribute in filter.attributes:
                        attrs[atribute.key] = atribute.value
                found = self.root.find_all(filter.tag, attrs)
                everything = Tag(name='div', attrs={'_class': 'everything'})
                for element in found:
                    everything.append(element)
        return everything
    
    def processContent(self, content):
        return content
    
    def extractContent(self,content):
        tags = []
        

    def show(self):
        """
        Extended display function for debugging.
        """
        super().show()
        print("reading:", self.reading)
        print("version:", self.version)
        print("tags:", len(self.tags))
        for tag in self.tags:
            print("   " + key + ": " + len(self.tags[key]))
            for attrib in self.tags[key].keys():
                print("   " + attrib + ": " + self.tags[key][attrib])
        return



class BibleAnalyser(WebAnalyser):
    """
    Analyse a Biblegateway web page
    """

    def __init__(self, reading, version="NIVUK"):  # default to English NIV
        self.version = version
        self.reading = reading
        url = "https://www.biblegateway.com/passage/"
        values = {"search": reading, "version": version}
        super().__init__(url, values=values)
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
    bible = BibleReading("Psalm 147:2,3", version="NLT")
    bible.showPassage()
    print()
    bible.htmlParas(None)
    print()
    bible.show()
    '''
    '''
    for i in range(1, 9):
        bible = BibleReading("song " + str(i), version="NLT")
        print(bible.getHtmlParas(reading=True))
    '''

    '''
    version="NLT"
    reading = "song 1"
    url = "https://www.biblegateway.com/passage/"
    values = {"search": reading, "version": version}
    tree = WebTree(url=url, values=values, output="song1.txt")
    '''
    '''
    version="NLT"
    reading = "psa 7"
    url = "https://www.biblegateway.com/passage/"
    values = {"search": reading, "version": version}
    tree = WebTree(url=url, values=values, output="psalm7.txt")
    passages = tree.root.findAll('div', class_="passage-text")
    copyrights = tree.root.findAll('div', class_="copyright-table")
    with open("psa7.txt", 'w', encoding = 'utf-8') as f:
        for passage in passages:
            f.write(passage.prettify())
        for copyright in copyrights:
            f.write(copyright.prettify())
    '''
    version="NIVUK"
    reading = "joh 1"
    url = "https://www.biblegateway.com/passage/"
    values = {"search": reading, "version": version}
    tree = WebTree(url=url, values=values, output="john1.txt")
    passages = tree.root.findAll('div', class_="passage-text")
    copyrights = tree.root.findAll('div', class_="copyright-table")
    with open("joh1.txt", 'w', encoding = 'utf-8') as f:
        for passage in passages:
            f.write(passage.prettify())
        for copyright in copyrights:
            f.write(copyright.prettify())


