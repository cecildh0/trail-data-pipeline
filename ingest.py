"""
This script is used to ingest the data.
It reads any csv paths given from main.py.
The output is a list of pandas dataframes.
"""

import os

import pandas as pd


def ingest(csv_paths):
    dataframes = []

    for csv in csv_paths:
        if not os.path.isfile(csv):
            print(f"File not found: {csv}")
            return []

        try:
            df = pd.read_csv(csv)
        except Exception as error:
            print(f"Could not read CSV {csv}: {error}")
            return []

        print(f"Ingested {len(df)} rows, {len(df.columns)} columns from {csv}")
        dataframes.append(df)

    return dataframes
