import torch
from model import *
from datetime import datetime
import pprint

# Create API with flask
from flask import Flask, request, jsonify

# Connect to MongoDB
from pymongo import MongoClient


# create flask app
app = Flask(__name__)

# connect to mongodb client
client = MongoClient('localhost', port=27017)
db = client.sentiment_analysis # create a database whose name is 'sentiment_analysis'
request_response = db.request_response # create a collection


# load the model
model_sentiment = torch.load('model6LSTM_snappfood')

# Check which device we are using
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


@app.route("/predict", methods=['POST'])
def predict():
    
    json_ = request.json
    preprocessed_input = data_preprocessing(json_["text"])

    vocab = read_vocab('SnappFood_Vocabulary.txt') # read vocabulary file 
    unk_idx = vocab.get('<unk>')

    # return preprocessed_input # to be sure that preprocessed_input is in your desired form

    indexed_input = [vocab.get(i, unk_idx) for i in preprocessed_input.split()] # converts to index or unk if not in vocab
    length = torch.LongTensor([len(indexed_input)]) 
    tensor = torch.LongTensor(indexed_input).to(device)
    tensor = tensor.unsqueeze(0)

    prediction = torch.round(model_sentiment(tensor, length).squeeze(0))

    # save request and response in json file
    request_response.insert_one({"text":json_["text"] ,
                                 "Sentiment":"SAD" if int(prediction.item())==1 else "HAPPY",
                                 "timestamp":datetime.now()})

    return jsonify({"text":json_["text"] , "Sentiment":"SAD" if int(prediction.item())==1 else "HAPPY"})

    

if __name__ == "__main__":
    app.run(debug=True)

    # for respose in request_response.find({"Sentiment"}):
    #     pprint.pprint(respose)
