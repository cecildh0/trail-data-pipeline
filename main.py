"""
This script is used to run the pipeline.
It ingests the data, transforms it, and outputs it to an S3 bucket.
"""

import os
from ingest import ingest
from output import output
from transform import transform
from validate import validate


BUCKET_NAME = os.getenv("BUCKET_NAME", "columbia-river-gorge-hiking-trails")
LOCAL_TRAILS_FILE = os.getenv(
    "LOCAL_TRAILS_FILE", "data/raw/HikingTrails_TheGorge.csv"
)
LOCAL_HAZARDS_FILE = os.getenv(
    "LOCAL_HAZARDS_FILE", "data/raw/Trail_hazards_danger.csv"
)
S3_TRAILS_KEY = os.getenv("S3_TRAILS_KEY", "raw/HikingTrails_TheGorge.csv")
S3_HAZARDS_KEY = os.getenv("S3_HAZARDS_KEY", "raw/Trail_hazards_danger.csv")
RAW_CSV_PATHS = [
    LOCAL_TRAILS_FILE,
    LOCAL_HAZARDS_FILE,
]


def download():
    try:
        import boto3

        s3 = boto3.client("s3")
        # Bucket, key, filename
        s3.download_file(BUCKET_NAME, S3_TRAILS_KEY, LOCAL_TRAILS_FILE)
        s3.download_file(BUCKET_NAME, S3_HAZARDS_KEY, LOCAL_HAZARDS_FILE)
        print("Downloaded raw files from S3.")
    except Exception as error:
        print(f"S3 download skipped: {error}")
        print("Using local raw files instead.")


def main():
    download()

    # Pipeline
    ingested_dataframes = ingest(RAW_CSV_PATHS)
    if len(ingested_dataframes) < 2:
        print("Need at least 2 csv files for current transform step.")
        return
    df_hiking_trails = ingested_dataframes[0]
    df_trail_hazards = ingested_dataframes[1]
    df_transformed = transform(df_hiking_trails, df_trail_hazards)
    if df_transformed is None:
        print("Transformed dataframe doesn't exist. Pipeline stopped after transform.")
        return
    validate(df_transformed)
    output()
    print("Pipeline finished.")


if __name__ == "__main__":
    main()