import torch
import pickle
import torchtext
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

import re
import string

from parsivar import Normalizer, Tokenizer, FindStems, POSTagger, FindChunks


#########################################################################################################
#################################### LSTM model for SnappFood dataset ###################################
#########################################################################################################

class SentimentAnalysis(nn.Module):
  def __init__(self, vocab_size, embedding_dim, hidden_dim, output_dim, 
               num_layers, dropout ):
    super(SentimentAnalysis, self).__init__()
    
    #embedding layer
    self.embedding = nn.Embedding(vocab_size, embedding_dim)
    
    #lstm layer
    self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers=num_layers, dropout=dropout, batch_first=True)

    #dense layer
    self.fc = nn.Linear(hidden_dim*2, output_dim)

    self.sigmoid = nn.Sigmoid()

  def forward(self, text, text_lengths):
    # text = [batch size, sent_len}
    embedded = self.embedding(text)
    # embedded = [batch_size, sent_len, emd dim]

    packed_embedded = nn.utils.rnn.pack_padded_sequence(embedded, text_lengths, batch_first=True)

    packed_out, (hidden, cell) = self.lstm(packed_embedded)
    #hidden = [batch size, num layers * num directions,hid dim]
    #cell = [batch size, num layers * num directions,hid dim]

    # concat the final forward and backward hidden state
    hidden = torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim=1)

    # hidden = [batch size, hid dim* num direction]
    dense_output=self.fc(hidden)

    # final activation funciton 
    outputs=self.sigmoid(dense_output)

    return outputs

#########################################################################################################
#################################### Preprocessing section ##############################################
#########################################################################################################

# define a function to read file
def readFile(filename):
  fileObj = open(filename, 'r', encoding='utf-8') # open the file in read mode
  words = fileObj.read().splitlines() # puts the file into an array
  fileObj.close()
  return words


# length of this file is 1370
stopwords = readFile('persian_stopwords_kharazi.txt')

# print(stopwords)

# Because, after stemming we have '&' in between of our verbs, we should delete them in function delete_and.
def delete_and(word):
  idx = word.find("&")
  if idx!=-1:
    word = word[:idx]
  return word


def data_preprocessing(review):
  try:
    # replace half-space with ' '
    review =  re.sub('\u200c', ' ',review)

    # Normalizing the text
    # First we should normalize text in order to convert persian numbers into english numbers then
    # with following function (filter) delete them
    # Because, some comments are pinglish, we should set pinglish_conversion_needed = True
    normalizer = Normalizer(pinglish_conversion_needed=True) 
    review = normalizer.normalize(review)

    # because after normalization appear some '/u200c', we should replace them with space
    review =  re.sub('\u200c', ' ',review)

    # delete english characters and numbers from sentences
    review = filter(lambda x: x in string.whitespace or x not in string.printable, review)
    review = ''.join(ch for ch in list(review))
    
    
    # word tokenization
    tokenizer = Tokenizer()
    words = tokenizer.tokenize_words(review)

    # stemming 
    stemmer = FindStems()
    review = [stemmer.convert_to_stem(word) for word in words]

    # we should delete '&', because after stemming we have '&' in between of our verbs
    review = [delete_and(word) for word in review]

    # remove stop words
    words_without_stopword = filter(lambda x: x not in stopwords, review)
    words_without_stopwords = list(words_without_stopword)
    
    # join words in preprocessed review
    review = ' '.join(words_without_stopwords)
    
    return review

  except TypeError:
    print(review)
    raise

#########################################################################################################
############################## word to index (TEXT.vocab.stoi[word]) section ############################
#########################################################################################################

# let's read TEXT.vocab file that we saved it from our notebook
def read_vocab(path):
    vocab = dict()
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            index, token = line.split('\t')
            vocab[token[:token.find('\n')]] = int(index)
    return vocab
