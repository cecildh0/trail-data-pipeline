"""
Output layer for the pipeline.
Handles publishing processed output artifacts.
"""

import os

BUCKET_NAME = os.getenv("BUCKET_NAME", "columbia-river-gorge-hiking-trails")
LOCAL_PROCESSED_FILE = os.getenv(
    "LOCAL_PROCESSED_FILE", "data/processed/trails_clean.csv"
)
S3_PROCESSED_KEY = os.getenv("S3_PROCESSED_KEY", "processed/trails_clean.csv")


def output():
    try:
        import boto3

        s3 = boto3.client("s3")
        # Local filename, bucket, key
        s3.upload_file(LOCAL_PROCESSED_FILE, BUCKET_NAME, S3_PROCESSED_KEY)
        print("Uploaded processed file to S3.")
    except Exception as error:
        print(f"S3 upload skipped: {error}")



