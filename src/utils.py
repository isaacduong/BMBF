import pandas as pd
import numpy as np


class BMBF:
    def __init__(self, file):
        self.data = pd.read_csv(file)

    def clean_data(self, data):

        """Clean data by removing NaN values .

        Args:
            data (pandas.DataFrame): Data to be cleaned.

        Returns:
            pandas.DataFrame: Cleaned data.
        """

        data = data.dropna()
        return data
