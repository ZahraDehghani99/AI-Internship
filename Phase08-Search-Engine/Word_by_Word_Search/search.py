# libraries for working with text
import re

# libraries for create API with flask
from flask import Flask, request, jsonify

# connet to mongodb
from pymongo import MongoClient

# Convert PyMongo Cursor to JSON
from bson.json_util import dumps 
from bson import json_util



# defien a function to display output in a desired form (title of new + 5 words after and before searched word)
def display_output(search_keyword, mongodb_document):
    
    search_keyword_lst = search_keyword.split()
    text_lst = re.split('\.| ', mongodb_document["doc_text"]) # split text based on . and space(split string with multiple delimiters)
    
    # list of first matching indexes
    match_index = []

    # find index of first matching for each word of search_keyword
    if len(match_index) == 0:
        for i in range(len(search_keyword_lst)):
            for j in range(len(text_lst)):
                if search_keyword_lst[i] in text_lst[j]:
                    match_index.append(j)
                

    surrounding_words = []
    # return str(-5+min(match_index))
    # Add 5 words before and 5 words after a searched word in surrounding_words
    # We use min(match_index), because we need first match
    # i + min(march_index) : if our seached word is at the beginnig of the new or at the end of the new
    # it doesnt't have neighbour before it or after it
    for i in range(-5, 6):
        if i + min(match_index) >= 0: ####
            surrounding_words.append(text_lst[i + min(match_index)])  

    output = " ".join(word for word in surrounding_words)

    return output  

###################################### create API #################################

# create flask app
app = Flask(__name__)

# connect to mongodb client to accest to created database
client = MongoClient('localhost', port=27017)
db = client.search_engine # switch to database whose name is 'search_engine'
ham = db.ham # switch to a collection whose name is 'ham'

# Create text index and allow text search over doc_text field
ham.create_index([('doc_text','text')])
        

# API for returning doc_title and words around search keyword in doc_text
@app.route("/search", methods=['POST'])
def search():

    # our input is a JSON file and it's pattern is as follow:
    # {text : ...}
    json_ = request.json
    search_keyword = json_["text"]

    # create list to store our output in it
    data = [{"search_keyword": search_keyword}]

    # return str(ham.find({"$text": { "$search": search_keyword}}, {"doc_id":0, "_id":0}).count())

    for record in ham.find({"$text": { "$search": search_keyword}}, {"doc_id":0, "_id":0}).sort([("score", {"$meta": "textScore"})]):

        text = display_output(search_keyword, record)
        title = record["doc_title"]
        data.append({'doc_title': title, 'doc_text':text})

    json_data = dumps(data, ensure_ascii=False, indent=4, sort_keys=True, default=str)
    
    # Writing data to file data.json
    with open('data.json', 'w', encoding='utf-8') as file:
        file.write(json_data)
    
    return json_data


if __name__ == "__main__":
    app.run(debug=True)