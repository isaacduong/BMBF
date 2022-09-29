import re
import traceback
import time
from logging import Logger

import pandas as pd

import requests
from bs4 import BeautifulSoup
from crossref_commons.retrieval import get_publication_as_json
from crossref_commons.iteration import iterate_publications_as_json


class crawler(object):
    def __init__(self, APIKey, max_results=10):

        self.APIKey = APIKey
        self.max_results = max_results

    def retrieve_metadata(self, funder="501100002347"):
        """This function retrieves metadata from crossref and returns a dataframe with the metadata.

        Args:
            funder (str, optional): number to identfy funder. Defaults to '501100002347' (BMBF number).
            max_results (int, optional): Number of publications retrieved from crossref. Defaults to 45000.

        Returns:
            pandas.DataFrame: dataframe from retrieved publications
            list: list of DOIS
        """

        metadatas = []
        filters = {"funder": funder}

        for i, p in enumerate(
            iterate_publications_as_json(max_results=self.max_results, filter=filters)
        ):
            pub = {}
            for f in p.get("funder"):
                if f.get("DOI") == "10.13039/501100002347":
                    pub["AWARD"] = f.get("award", "")
                    break
            pub["DOI"] = p.get("DOI", "")
            pub["TITLE"] = p.get("title", "")
            pub["ABSTRACT"] = p.get("abstract", "")
            if ("resource" in p.keys()) and ("primary" in p["resource"].keys()):
                pub["RESOURCE"] = p["resource"]["primary"].get("URL", "")
            else:
                pub["RESOURCE"] = ""

            metadatas.append(pub)

        df = pd.DataFrame.from_records(metadatas)
        df.to_csv("./data/metadata.csv", index=False)

        return df, df["DOI"].tolist()

    def extract_abstract(self, DOI):

        """This function extracts the abstract from the DOI.

        Args:
            DOI(string): DOI to extract abstract from

        """

        def extract_abstract_from_elsevier(DOI, APIKey):
            """This function extracts the abstract from the elsevier.

            Args:
                DOI (string): DOI to extract abstract from
                APIKey (str, optional): personal APIKey provided by elsevier.
            Returns:
                string: abstract of publication published by elsevier.
            """

            resource = (
                "https://api.elsevier.com/content/article/doi/%s?httpAccept=text/xml&APIKey=%s"
                % (DOI, APIKey)
            )
            try:
                res = requests.get(resource, timeout=10)
                soup = BeautifulSoup(res.text, "html.parser")
                abstract = soup.find("dc:description").text
                return abstract
            except:
                Logger.error(f"Unable to retrieve {DOI} from {resource}")
                return ""

        def extract_abstract_from_other_source(DOI):
            """This function extracts the abstract from the other sources."""

            resource = "https://www.doi.org/" + DOI
            try:
                res = requests.get(
                    resource,
                    timeout=10,
                )
                soup = BeautifulSoup(res.text, "html.parser")
                attrs = [
                    {"name": "dc.description"},
                    {"name": "description"},
                    {"property": "og:description"},
                    {"name": "citation_abstract"},
                ]
                for attr in attrs:
                    meta_tag = soup.find("meta", attrs=attr)
                    if meta_tag:
                        abstract = meta_tag["content"]
                        return abstract
            except:
                Logger.error(f"Unable to retrieve {DOI} from {resource}")
                return ""

        if DOI.startswith("10.1016"):  #
            return extract_abstract_from_elsevier(DOI, self.APIKey)

        else:
            return extract_abstract_from_other_source(DOI)
