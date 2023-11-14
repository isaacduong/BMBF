import string
import pandas as pd
import re
import langdetect
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize


def clean_data(data: pd.DataFrame):
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
    tokens = [word for word in nltk.word_tokenize(text) if word not in stop_words and word not in string.punctuation]
    stems = [stemmer.stem(t) for t in tokens]

    return stems


def remove_html_tags(text):

    """Remove html tags from a string"""
    clean = re.compile("<.*?>")

    return re.sub(clean, "", text)

def remove_url(text):
    
    pattern = r"https?://[^\s]+"
    text_without_urls = re.sub(pattern, '', text)
    return text_without_urls


def detect_language(text):
    """Detects the language of the given text.

  Args:
    text: A string containing the text to be analyzed.

  Returns:
    A string containing the language code of the detected language.
  """

    lang = langdetect.detect(text)
    return lang

def split_entries_in_column(df, column_name):
    # Duplicate rows with multiple values in the specified column
    df_split = df.copy()
    df_split[column_name] = df_split[column_name].str.split('[&|;]')

    # Explode the lists in the specified column to create multiple rows
    df_split = df_split.explode(column_name)

    return df_split

def extract_FKZ(FKZ):

    """Extract the FKZ from a string"""
    pattern = "[A-Z0-9/]{3,10}"
    matches = re.findall(pattern, FKZ)

    return matches[0] if matches else None

