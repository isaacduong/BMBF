import asyncio
from collections import defaultdict
import io
import re
import traceback
import time
import logging

logging.basicConfig(level=logging.DEBUG, format="{asctime} {message}", style="{")


import pandas as pd
from PyPDF2 import PdfFileReader

import requests
import aiohttp
from bs4 import BeautifulSoup
from crossref_commons.retrieval import get_publication_as_json
from crossref_commons.iteration import iterate_publications_as_json


class PublisherProperties:

    mdpi = {"attrs": {"class": "html-body"}}

    nature = {"attrs": {"class": "main-content"}, "split_text": "Data availability"}

    frontiersin = {
        "attrs": {"class": "JournalFullText"},
        "split_text": "Conflict of Interest",
    }


class crawler(object):
    """This class contains some functions to fetch DOIS from Crossref and
    using these DOIS to retrieve abstracts as wwell as full texts from different sources

    Args:
        APIKey (str): personal APIKey provided by elsevier to retrieve datas from sciencedirect / elsevier.
    """

    def __init__(self, APIKey, max_results=10):

        self.APIKey = APIKey
        self.max_results = max_results
        self.abstracts = defaultdict(str)
        self.fulltexts = defaultdict(str)
        self.html_contents = defaultdict(str)

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
                dict: dictionary contains the abstract of publication published by elsevier.
            """

            resource = (
                "https://api.elsevier.com/content/article/doi/%s?httpAccept=text/xml&APIKey=%s"
                % (DOI, APIKey)
            )
            try:
                res = requests.get(resource, timeout=10)
                soup = BeautifulSoup(res.text, "html.parser")
                abstract = soup.find("dc:description").text
                self.abstracts[DOI] = abstract

            except Exception as ex:
                ex.print_exc()
                logging.error(f"Unable to retrieve {DOI} from {resource}")

            finally:
                return self.abstracts

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
                        self.abstracts[DOI] = meta_tag["content"]

            except Exception as ex:
                logging.error(f"Unable to retrieve {DOI} from {resource}")
                ex.print_exc()

            finally:
                return self.abstracts

        if DOI.startswith("10.1016"):
            return extract_abstract_from_elsevier(DOI, self.APIKey)

        else:
            return extract_abstract_from_other_source(DOI)

    def extract_pdf(self, url):
        """This function extracts the pdf from the url.

        Args:
            url (string): url to extract pdf from

        Returns:
            string: pdf of publication
        """
        text = []
        try:
            r = requests.get(url, timeout=10)
            f = io.BytesIO(r.content)
            reader = PdfFileReader(f)
            for page in range(reader.getNumPages()):

                text.append(reader.getPage(page).extractText())
                if "Acknowledgements" in reader.getPage(page).extractText():
                    break

        except Exception as ex:
            traceback.print_exception(type(ex), ex, ex.__traceback__)
            logging.error(f"Unable to retrieve {url}")

        finally:
            self.fulltexts[url] = "".join(text)
            return self.fulltexts

    def extract_fulltext_from_elsevier(self, DOI):
        """This function extracts the fulltext from the elsevier site.

        Args:
            DOI (strings):      DOI to extract fulltext from

        Returns:
            dict: dictionary contains fulltexts
        """
        resource = (
            "https://api.elsevier.com/content/article/doi/%s?httpAccept=text/xml&APIKey=%s"
            % (DOI, self.APIKey)
        )
        fulltext = ""
        try:
            res = requests.get(resource, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            openaccess = True == int(soup.find("openaccess").text)
            if openaccess:
                sections_tag = soup.find("ce:sections")
                resultset = sections_tag.findChildren()
                for text in resultset:
                    fulltext = fulltext + str(text)
                self.fulltexts[DOI] = fulltext

        except Exception as ex:
            traceback.print_exc()
            logging.error(f"Unable to retrieve {DOI} from {resource}")

        finally:
            return self.fulltexts

    def extract_fulltext(self, url):
        """This function extracts the fulltext from urls by publishers mdpi, nature and frontiersin.

        Args:
            url (strings): url to extract

        Returns:
            dict: dictionary contains fulltexts
        """

        fulltext = ""
        if "mdpi" in url:
            url = url + "/htm"  # fulltext suffix

        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            if "nature" in url:
                if soup.find("span", attrs={"data-test": "open-access"}):
                    resultset = soup.find(
                        "div", attrs=PublisherProperties.nature["attrs"]
                    ).findChildren()

                    for text in resultset:
                        fulltext = fulltext + str(text)
                    self.fulltexts[url] = fulltext.split(
                        PublisherProperties.nature["split_text"]
                    )[0]
            elif "mdpi" in url:
                resultset = soup.find(
                    "div", attrs=PublisherProperties.mdpi["attrs"]
                ).findChildren()
                for text in resultset:
                    fulltext = fulltext + str(text)
                self.fulltexts[url] = fulltext

            elif "frontiersin" in url:
                resultset = soup.find(
                    "div", attrs=PublisherProperties.frontiersin["attrs"]
                ).findChildren()

                for text in resultset:
                    fulltext = fulltext + str(text)
                self.fulltexts[url] = fulltext.split(
                    PublisherProperties().frontiersin["split_text"]
                )[0]

        except Exception as ex:
            traceback.print_exc()
            logging.error(f"Unable to retrieve {url}")

        finally:
            return self.fulltexts

    async def main(self, urls):

        """function to retrieve html sites synchroniously"""

        async def retrieve_text(session, url):
            try:
                async with session.get(url) as res:
                    self.html_contents[url] = await res.text()

            except Exception as ex:

                traceback.print_exception(type(ex), ex, ex.__traceback__)
                self.html_contents[url] = None

        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in urls:
                task = asyncio.ensure_future(retrieve_text(session, url))
                tasks.append(task)

            await asyncio.gather(*tasks)
