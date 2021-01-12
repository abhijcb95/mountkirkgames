import os
import time

gcs_bucket = os.environ.get("GCS_BUCKET")

if not gcs_bucket:
    print("Please use 'export GCS_BUCKET={new bucket name}' using a bucket for dataflow")
    exit()
os.system("gsutil cp -r gcs-to-bq/temp/ gcs-to-bq/dataflow_scripts/ gcs-to-bq/test.txt gs://{}/".format(gcs_bucket))