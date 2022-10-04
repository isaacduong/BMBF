from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer


DATA_FILE = "../data/BMBF.csv"
FULLTEXT_DATA_FILE = "../data/BMBFaenrichment.csv"
LOG_CONFIG_FILE = "../log_config.yaml"

models = {
    "kmeans": KMeans(),
    "DBSCAN": DBSCAN(),
    "agglomerativeclustering": AgglomerativeClustering(),
}

vectorizers = {
    "countVectorizer": CountVectorizer(),
    "tfidfVectorizer": TfidfVectorizer(),
}
