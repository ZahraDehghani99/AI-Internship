from parsivar import Normalizer, Tokenizer, FindStems
import re
import string

######################################### text preprocessing functions #############################

# define a function to read file
def readFile(filename):
  fileObj = open(filename, 'r', encoding ='utf-8') # open the file in read mode
  words = fileObj.read().splitlines() # puts the file into an array
  fileObj.close()
  return words

stopwords = readFile('/Users/User/Flask_Basics/persian_stopwords_kharazi.txt')  

# Because, after stemming we have '&' in between of our verbs, we should delete them in function delete_and.
def delete_and(word):
  idx = word.find("&")
  if idx!=-1:
    word = word[:idx]
  return word


def data_preprocessing(review, stopwords):
  try:
    # replace half-space with ' '
    review =  re.sub('\u200c', ' ',review)

    # Normalizing the text
    # First we should normalize text in order to convert persian numbers into english numbers then
    # with following function (filter) delete them
    # Because, some comments are pinglish, we should set pinglish_conversion_needed = True
    normalizer = Normalizer() 
    review = normalizer.normalize(review)

    # because after normalization appear some '/u200c', we should replace them with space
    review =  re.sub('\u200c', ' ',review)

    # delete english characters and numbers from sentences
    review = filter(lambda x: x in string.whitespace or x not in string.printable, review)
    review = ''.join(ch for ch in list(review))
    
    if review != ' ':
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



