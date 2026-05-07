# Trail Data Pipeline Project

End-to-end data pipeline for trail data on trails in Columbia River Gorge. Uses Python, pandas, and AWS (specifically S3 buckets), in ingest -> transform -> output format

Raw CSV data files used for this project come from [Hiking Trails, Columbia River Gorge by CHUCKH](https://www.kaggle.com/datasets/chuckh193333/hiking-trails-columbia-river-gorge) on Kaggle.

## What it does

Designed for two CSVs: hiking trails (specifically Columbia River Gorge) and trail hazards (for those same trails). It merges them, cleans up messy text/numbers and standardizes data, writes a cleaned CSV, and uploads that file to S3. If S3 download or upload fails, it prints a message and falls back to local files and upload.


## Run

From this folder:

```bash
pip install -r requirements.txt
python main.py
```

You should have the S3 credentials configured as well so raw data files can be downloaded and processed the data file can be uploaded. If you don't have these, you need the raw CSVs under data/raw/ but in this case nothing will be uploaded to the S3 bucket.

Test:

```bash
python -m unittest test_transform.py
```

## Env vars

If you don’t set these, the code uses the defaults

| Variable | Use |
|----------|----------------|
| `BUCKET_NAME` | S3 bucket |
| `LOCAL_TRAILS_FILE` | Where to save/read trails CSV locally |
| `LOCAL_HAZARDS_FILE` | Where to save/read hazards CSV locally |
| `S3_TRAILS_KEY` | Object key for trails in the bucket |
| `S3_HAZARDS_KEY` | Object key for hazards in the bucket |
| `LOCAL_PROCESSED_FILE` | Local path `output.py` uploads from (should match what `transform.py` writes — right now that’s `data/processed/trails_clean.csv` in code) |
| `S3_PROCESSED_KEY` | Where to upload the cleaned file in S3 |

## Pipeline Diagram

```
                    +------------------+
                    |        S3        |
                    |  raw CSV objects |
                    +--------+---------+
                             |
                      download (boto3)
                             |
                             v
                       +---------------+     
                       |    ingest     | 
                       |  read csv(s)  |     
                       +---------------+    
                               |
                               |
                               v
                       +------------------+     
                       |    transform     | 
                       | merge dataframes |
                       |  and clean data  |   
                       +------------------+
                               |
                               |
                               v
                        +---------------+     
                        |    validate   |    
                        +---------------+    
                               |
                               |
                               v
                        +---------------+
                        |   output      |
                        |  S3 upload    |
                        +---------------+
```


## Layout

- `main.py` — Runs download from S3 and ingest -> transform -> validate -> output pipeline
- `ingest.py` — Load CSVs into dataframes, reusable for any csv(s) 
- `transform.py` — Cleaning and merge of the two dataframes
- `validate.py` — Checks before publish  
- `output.py` — Upload processed CSV to S3


