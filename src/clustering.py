import re
import logging
from logging import config
import yaml
from typing import Any
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import DBSCAN

import dataenrichment
import nltk

# nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize

from sklearn.metrics import silhouette_score
from utils import remove_html_tags

logger = logging.getLogger(__name__)


class Cluster(object):

    """class for clustering the data"""

    def __init__(self, vectorizer, clusterer):

        logger.info("initializing clusterer")
        self.vectorizer = vectorizer
        self.clusterer = clusterer

    def fit_transform(self, data, *args: Any, **kwds: Any) -> Any:

        logger.info("fitting data")
        self.X_vec_ = self.vectorizer.fit_transform(data, *args, **kwds)
        clusters = self.clusterer.fit(self.X_vec_)

        return clusters.labels_

    def silhouette_score(self, labels):

        if not self.X_vec_:
            raise ValueError("data must be fitted first")

        logger.info("calculating silhouette score")
        silhouette_s = silhouette_score(self.X_vec, labels)

        return silhouette_s
