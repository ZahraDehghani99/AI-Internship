import torch
from model import *
from flask import Flask, request, jsonify

# create flask app
app = Flask(__name__)

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

    indexed_input = [vocab.get(i, unk_idx) for i in preprocessed_input.split()] # converts to index or unk if not in vocab
    length = torch.LongTensor([len(indexed_input)]) 
    tensor = torch.LongTensor(indexed_input).to(device)
    tensor = tensor.unsqueeze(0)

    prediction = torch.round(model_sentiment(tensor, length).squeeze(0))

    return jsonify({"text":json_["text"] , "Sentiment":"SAD" if int(prediction.item())==1 else "HAPPY"})

    

if __name__ == "__main__":
    app.run(debug=True)