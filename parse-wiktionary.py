"""
$ pip3 install defusedxml
$ pip3 install regex
"""

import time
import xml

import regex
from defusedxml.sax import parse


# https://www.tutorialspoint.com/parsing-xml-with-sax-apis-in-python
class WiktHandler(xml.sax.ContentHandler):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.text = ""
        self.timestamp = ""
        self.id = ""
        self.tag = ""
        self.locator = None

    def setDocumentLocator(self, locator):
        self.locator = locator

    def startElement(self, tag, attributes):
        self.tag = tag

        if tag == "page":
            print("new page line {0}".format(self.locator.getLineNumber()))
            self.title = ""
            self.text = ""
            self.timestamp = ""
            self.id = ""

    def endElement(self, tag):
        self.tag = "***"
        if tag == "page":
            # https://stackoverflow.com/questions/4324790/removing-control-characters-from-a-string-in-python
            title = regex.sub(r'\p{C}', '', self.title)
            print("end page {3}: '{0}' len {1} @ {2}".format(title, len(self.text), self.timestamp, self.id))
                
    def characters(self, content):

        if self.tag == "title":
            self.title = content
        elif self.tag == "timestamp":
            self.timestamp = content
        elif self.tag == "id" and self.id == "":
            self.id = content
        elif self.tag == "text":
            self.text += content


start_time = time.time()

xmlfile = 'enwiktionary-20220120-pages-meta-current.xml'
handler = WiktHandler()
wikt = parse(xmlfile, handler)

end_time = time.time()
print("seconds: {0}".format(end_time - start_time))
