import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize


def cleaned_data(data: pd.DataFrame):
    """
    Args:
        data (pd.DataFrame): data to clean

    Returns:
        pd.DataFrame: cleaned data
    """

    columns = [c.replace('"', "").replace("=", "") for c in data.columns]
    data.columns = columns
    data.drop("Unnamed: 26", axis=1, inplace=True)
    # remove invalid token in columns values
    for col in columns[:-1]:
        data[col] = data[col].apply(lambda v: v.replace('"', "").replace("=", ""))

    data["FKZ"] = data["FKZ"].apply(lambda s: s.replace(" ", ""))

    return data


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


def remove_html_tags(text):

    """Remove html tags from a string"""
    clean = re.compile("<.*?>")

    return re.sub(clean, "", text)


def extract_FKZ(FKZ):

    """Extract the FKZ from a string"""
    pattern = "[A-Z0-9/]{3,10}"
    matches = re.findall(pattern, FKZ)

    return matches if matches else None


def extract_url(link):

    """Extract the url from a string"""
    # pattern = "https?://[^\s]+"
    pattern = r"https?://[/0-9a-z-]+\.[a-z-]+\.?[a-z]*[\.a-z]*"
    url = re.findall(pattern, link)

    return url[0] if url else None
