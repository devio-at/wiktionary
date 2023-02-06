"""
$ pip3 install defusedxml
$ pip3 install regex
"""

import sys
import time
import xml
from dataclasses import dataclass

import psycopg2
import regex
from defusedxml.sax import parse


@dataclass
class WikiSite:
    sitename: str
    dbname: str
    base: str
    case: str
    id: int

@dataclass
class Namespace:
    key: str
    case: str
    name: str
    id: int

@dataclass
class Page:
    id: str
    namespace: str
    title: str
    timestamp: str
    text: str


con = psycopg2.connect("host='localhost' dbname='wiktionary' user='pguser' password='pg'")
cur = con.cursor()

language_id = 'en'
xmlfile = '../enwiktionary-20220120-pages-meta-current.xml'
source = 'enwiktionary-20220120-pages-meta-current.xml'

# https://www.tutorialspoint.com/parsing-xml-with-sax-apis-in-python
class WiktHandler(xml.sax.ContentHandler):
    def __init__(self):
        super().__init__()
        self.tag = ""
        self.locator = None
        self.wikisite = None
        self.namespace = None
        self.page = None
        self.revision = None

    def setDocumentLocator(self, locator):
        self.locator = locator

    def startElement(self, tag, attributes):
        self.tag = tag

        if tag == "siteinfo":
            self.wikisite = WikiSite("", "", "", "", None)

        if tag == "namespaces":
            cur.execute("""
            INSERT INTO public.wikisite (language_id, filename, sitename, dbname, base, case_sensitive)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
            """, (
                language_id, source, 
                self.wikisite.sitename, self.wikisite.dbname, self.wikisite.base, self.wikisite.case == 'case-sensitive'
            ))
            con.commit()
            self.wikisite.id = cur.fetchone()[0]
            print("wikisite {0}".format(self.wikisite.id))

        if tag == "namespace":
            print("new namespace {0} {1} @{2}".format(attributes["key"], attributes["case"], self.locator.getLineNumber()))
            self.namespace = Namespace(attributes["key"], attributes["case"], "", None)

        if tag == "page":
            print("new page line {0}".format(self.locator.getLineNumber()))
            self.page = Page("", "", "", "", "")
            self.revision = None

        if tag == "revision":
            self.revision = "revision"

    def endElement(self, tag):
        self.tag = "***"

        if tag == "namespace":
            cur.execute("""
            INSERT INTO public.wikinamespace (site_id, "key", case_sensitive, "name")
            VALUES(%s, %s, %s, %s)
            """, (
                self.wikisite.id, self.namespace.key, self.namespace.case == 'case-sensitive', self.namespace.name
            ))
            con.commit()
            self.namespace = None

        if tag == "page":
            # https://stackoverflow.com/questions/4324790/removing-control-characters-from-a-string-in-python
            title = regex.sub(r'\p{C}', '', self.page.title)
            print("end page {3}: '{0}' len {1} @ {2}".format(title, len(self.page.text), self.page.timestamp, self.page.id))

            cur.execute("""
            INSERT INTO public.page
                (site_id, language_id, page_id, namespace_key, title, "timestamp", page_text)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (
                self.wikisite.id, language_id, 
                self.page.id, self.page.namespace, self.page.title, self.page.timestamp, self.page.text
            ))            
            con.commit()
            self.page = None
                
    def characters(self, content):

        if self.namespace != None:
            if self.tag == "namespace":
                self.namespace.name += content
        
        elif self.page != None:
            if self.tag == "title":
                self.page.title += content
            elif self.tag == "timestamp":
                self.page.timestamp += content
            elif self.tag == "id" and self.revision == None:
                self.page.id += content
            elif self.tag == "text":
                self.page.text += content
            elif self.tag == "ns":
                self.page.namespace += content

        elif self.wikisite != None:
            if self.tag == "sitename":
                self.wikisite.sitename += content
            elif self.tag == "dbname":
                self.wikisite.dbname += content
            elif self.tag == "base":
                self.wikisite.base += content
            elif self.tag == "case":
                self.wikisite.case += content


start_time = time.time()

handler = WiktHandler()
wikt = parse(xmlfile, handler)

con.commit()
cur.close()
con.close()

end_time = time.time()
print("seconds: {0}".format(end_time - start_time))
