from functions import *

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# libraries for create API with flask
from flask import Flask, request, jsonify

# connet to mongodb
from pymongo import MongoClient

# Convert PyMongo Cursor to JSON
from bson.json_util import dumps 
from bson import json_util



# load preprocessed dataframe . we preprocessed text in search_tfidf.ipynb.
df= pd.read_pickle(r'/Users/User/Flask_Basics/Search_Engine/TF-IDF/df_clean')

# Create Vocabulary
vocabulary = set()

# find unique words in whole of the documents and append them to vocabulary
for doc in df.clean_text:
    vocabulary.update(doc.split())


# Intializating the tfIdf model
tfidf = TfidfVectorizer(vocabulary=vocabulary)
tfidf_tran = tfidf.fit_transform(df['clean_text'])# Fit and Transform the TfIdf model


# we shoud define a function that applying data_preprocessing funtion on the input query and then create vector of shape (n_docs, n_vocabulary) for it.
# Then find similarity of input query vector and each document vector with cosine_similarity function .
# This function returns top 10 results .

def find_similarity(query):
    #apply preprocessing on the input query
    clean_query = data_preprocessing(query, stopwords)
    # create query vector using tfidf model
    query_vec = tfidf.transform([clean_query]) # Ip -- (n_docs,x), Op -- (n_docs,n_Feats) 
    # calculate inner product of each document vector and query vector
    # tfidf_tran : matrix of documents -- shape (n_docs, n_vocabulary=n_feats)
    results = cosine_similarity(tfidf_tran, query_vec).reshape((-1,)) # Op -- (n_docs,1) -- Cosine Sim with each doc

    results_lst = list(results)# use for show the score of each doc
    results_lst.sort() 

    # create dataframe for our output
    result_df = pd.DataFrame()
    # sort results array then use 10 elements of it from the end of the list then reverse it to have increasing order
    # np.argsort :  Returns the indices that would sort an array
    # we can change 10 to any number we want 
    out = results.argsort()[-10:][::-1]
    
    # add columns to the dataframe
    # index: index of a document
    for i,index in enumerate(out):
        result_df.loc[i,'index'] = str(index)
        result_df.loc[i,'title'] = df['title'][index]
        result_df.loc[i, 'text'] = df['text'][index]
    for j,simScore in enumerate(results_lst[-10:][::-1]):
        result_df.loc[j,'Score'] = simScore

    return result_df

###################################### create API #################################

# create flask app
app = Flask(__name__)

# connect to mongodb client to accest to created database
client = MongoClient('localhost', port=27017)
db = client.search_engine # switch to database whose name is 'search_engine'
ham_2007 = db.ham_2007 # switch to a collection whose name is 'ham'



# API for returning doc_title and words around search keyword in doc_text
@app.route("/search", methods=['POST'])
def search():

    # our input is a JSON file and it's pattern is as follow:
    # {text : ...}
    json_ = request.json
    search_keyword = json_["text"]

    # create list to store our output in it
    data = [{"search_keyword": search_keyword}]

    for i in range(find_similarity(search_keyword).shape[0]):
        
        title = find_similarity(search_keyword)['title'][i]
        text = find_similarity(search_keyword)['text'][i]
        score = find_similarity(search_keyword)['Score'][i]

        data.append({'doc_title': title, 'doc_text':text, 'doc_score':score})

    json_data = dumps(data, ensure_ascii=False, indent=4, sort_keys=True, default=str)   

    # Writing data to file data.json
    with open('data.json', 'w', encoding='utf-8') as file:
        file.write(json_data)
    
    return json_data 



if __name__ == "__main__":
    app.run(debug=True)
