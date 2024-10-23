import string
import re

import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import json


def preprocessor_text(text):
    """ pre-process text by removing punctuations, stopwords, stemming and tokenizing the text"""

    stop_words = stopwords.words('english')
    stemmer = PorterStemmer()
    text = str(text)
    text = text.lower()
    strip_punctuation = str.maketrans('', '', string.punctuation)
    text = text.translate(strip_punctuation)
    text = word_tokenize(text)
    processed_word = [stemmer.stem(word) for word in text if word not in stop_words]
    return processed_word


def concat(*args):
    concatenated_text = ""
    for arg in args:
        concatenated_text += str(arg) + " "
    return concatenated_text


# preprocessing data before indexing
def document_preprocessor(doc):
    with open(doc, 'r') as f:
        data_pub = json.load(f)
        document_pub = pd.DataFrame(data_pub)
        document_pub['words'] = document_pub[['abstract', 'title', 'authors_name','publication_date']].apply(
            lambda x: concat(x['abstract'], x['title'], x['authors_name'],x['publication_date']), axis=1)
        document_pub['words'] = document_pub['words'].apply(preprocessor_text)
        return document_pub

