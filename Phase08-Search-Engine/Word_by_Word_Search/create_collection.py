# connet to mongodb
from pymongo import MongoClient

# Library for parsing XML
import xml.etree.ElementTree as ET
import re


# connect to mongodb client
client = MongoClient('localhost', port=27017)
db = client.search_engine # create a database whose name is 'search_engine'
ham = db.ham # create a collection


# parse xml file
tree = ET.parse('HAM2-070101.xml')
root = tree.getroot()

# write xml file on database 
for elem in root.findall("DOC"):
    rows = []

    # parse DOCID
    doc_id = elem.find("DOCID")
    if doc_id != None:
        doc_id = doc_id.text
    rows.append(doc_id)
        
    # parse TITLE
    title = elem.find("TITLE")
    if title != None:
        title = re.sub('\n', ' ', title.text)
    rows.append(title)  

    # parse TEXT
    sent = elem.find("TEXT")
    if sent != None:
        sentence = list(sent)[-1].tail.strip() if list(sent) else sent.text.strip()
        sentence = re.sub('\n', ' ', sentence)
    rows.append(sentence)

    # save id, title and text of a news in json file
    ham.insert_one({"doc_id":rows[0] , "doc_title":rows[1], "doc_text":rows[2]})

