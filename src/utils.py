import pandas as pd
import re


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
