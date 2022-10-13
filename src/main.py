import argparse
import logging
from logging import config

import inspect
import yaml
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer

from clustering import Cluster
import config as con
import utils


def setup_logger(config_file):

    with open(config_file, "r") as f:
        log_config = yaml.safe_load(f.read())
        config.dictConfig(log_config)

    logger = logging.getLogger(__name__)
    return logger


def main(
    clusterer,
    vectorizer,
    preprocess,
    n_clusters,
    eps,
    min_sample,
    affinity,
    linkage,
    random_state,
    n_jobs,
    n_samples,
):

    logger = setup_logger(con.LOG_CONFIG_FILE)

    BMBF = pd.read_csv(con.DATA_FILE, encoding="latin1", sep=";")
    BMBF = utils.cleaned_data(BMBF)
    topics = (
        BMBF.loc[BMBF["Ressort"] == "BMBF", "Thema"]
        if n_samples == 0
        else BMBF.loc[BMBF["Ressort"] == "BMBF", "Thema"].iloc[:n_samples]
    )

    if clusterer == "kmeans":
        clusterer = KMeans(n_clusters=n_clusters, random_state=random_state)

    elif clusterer == "DBSCAN":
        clusterer = DBSCAN(eps=eps, min_samples=min_sample, n_jobs=n_jobs)

    elif clusterer == "agglomerativeclustering":
        clusterer = AgglomerativeClustering(
            n_clusters=n_clusters,
            affinity=affinity,
            linkage=linkage,
        )
    else:
        raise ValueError("Unknown clusterer")

    preprocessor = utils.preprocessor if preprocess else None
    if vectorizer == "countVectorizer":
        vec = CountVectorizer(preprocessor=preprocessor)
    elif vectorizer == "tfidfVectorizer":
        vec = TfidfVectorizer(preprocessor=preprocessor)

    cluster = Cluster(vec, clusterer)
    labels = cluster.fit_transform(topics)

    print(
        pd.DataFrame(
            {
                "Thema": topics,
                "Cluster": labels,
            }
        )
    )

    logger.info(f"silhouette score: {cluster.silhouette_score(labels)}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--clusterer", type=str)
    parser.add_argument("--vectorizer", type=str)
    parser.add_argument("--preprocess", default=False, type=bool)
    parser.add_argument("--n_clusters", default=8, type=int)
    parser.add_argument("--eps", default=0.5, type=int)
    parser.add_argument("--min_sample", default=5, type=int)
    parser.add_argument("--affinity", default="euclidean", type=str)
    parser.add_argument("--linkage", default="ward", type=str)
    parser.add_argument("--random_state", default=None, type=int)
    parser.add_argument("--n_jobs", default=None, type=int)
    parser.add_argument("--n_samples", default=500, type=int)

    args = parser.parse_args()

    main(
        args.clusterer,
        args.vectorizer,
        args.preprocess,
        args.n_clusters,
        args.eps,
        args.min_sample,
        args.affinity,
        args.linkage,
        args.random_state,
        args.n_jobs,
        args.n_samples,
    )
