# BMBF 
I developed this project for my bachelor's thesis, addressing an unsupervised machine learning problem. The main objective of the thesis is to explore how BMBF grants in the BMBF funding dataset can be grouped using cluster analysis. Additionally, the thesis aims to enrich the grants' data with information collected from selected sources and analyze the impact of data enrichment on the clustering results.

To achieve these goals, the research involves investigating various cluster analysis techniques to determine the most suitable one for grouping the grants. The thesis also aims to analyze whether the data enrichment process improves the quality of clustering. In this regard, several sources, namely NewsAPI, Crossref, altmetric, and idw (Informationsdienst Wissenschaft), will be utilized for data enrichment.

The thesis extensively utilizes natural language processing (NLP) techniques since the clustering is applied on text data. Alongside the Sklearn API, scipy which is employed for clustering, the thesis employs the nltk library for text preprocessing. Additionally, several other libraries such as aiohttp, asyncio, and Beautifulsoup are used for data enrichment. The crossref_common library is utilized for extracting open-source data from Crossref.

By leveraging these tools and methodologies, the thesis aims to provide insights into the grouping of BMBF grants using cluster analysis and evaluate the impact of data enrichment on the clustering results.
