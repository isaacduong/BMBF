import re
from typing import Any
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import DBSCAN

import nltk

# nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import silhouette_score


class cluster(object):

    """class for clustering the data"""

    def __init__(self, data, vectorizer=TfidfVectorizer(), clusterer=KMeans()):

        self.X = data
        self.vectorizer = vectorizer
        self.clusterer = clusterer

    def __call__(self, data, *args: Any, **kwds: Any) -> Any:

        X_vec = self.vectorizer.fit_transform(data, *args, **kwds)
        clusters = self.clusterer.fit(X_vec)

        return clusters.labels_


def preprocess(text):
    """
    Args:
        text (string): text to be preprocessed

    Returns:
        : stems of the text
    """
    stop_words = set(stopwords.words("german"))
    stemmer = SnowballStemmer("german")
    tokens = [word for word in nltk.word_tokenize(text) if word not in stop_words]
    stems = [stemmer.stem(t) for t in tokens]

    return stems
