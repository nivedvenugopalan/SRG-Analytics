import nltk
from nltk.stem import WordNetLemmatizer


import json


class stopwords:
    def __init__(self) -> None:
        # BASIC_STOP_WORDS
        self.NLTK = set(nltk.corpus.stopwords.words('english'))

        # ADVANCED_STOP_WORDS
        # in ./data/MAT/stopwords.txt
        with open('./data/MAT/stopwords.txt') as f:
            self.KAGGLE_1 = set(f.read().splitlines())


wnl = WordNetLemmatizer()
