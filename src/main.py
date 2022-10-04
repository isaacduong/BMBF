import os
import argparse
import logging
from logging import config


import yaml
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import silhouette_score

from clustering import Cluster
import dataenrichment
import dispatcher
from utils import cleaned_data, preprocess


def setup_logger(config_file):

    with open(config_file, "r") as f:
        log_config = yaml.safe_load(f.read())
        config.dictConfig(log_config)

    logger = logging.getLogger(__name__)
    return logger


def main(clusterer, vectorizer):

    logger = setup_logger(dispatcher.LOG_CONFIG_FILE)

    BMBF = pd.read_csv(dispatcher.DATA_FILE, encoding="latin1", sep=";")
    BMBF = cleaned_data(BMBF)

    clusterer = dispatcher.models[clusterer]
    vectorizer = dispatcher.vectorizers[vectorizer]

    cluster = Cluster(vectorizer, clusterer)
    label_ = cluster.fit_transform(BMBF.loc[BMBF["Ressort"] == "BMBF", "Thema"][:50])

    logger.info(f"silhouette score: {cluster.silhouette_score(label_)}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--clusterer", type=str)
    parser.add_argument("--vectorizer", type=str)

    args = parser.parse_args()
    main(args.clusterer, args.vectorizer)
