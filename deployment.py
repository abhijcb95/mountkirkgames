import os
import time
import datetime

def check_for_deployment_completion():
    os.system("export DEPLOYMENT_COMPLETE=$(gcloud deployment-manager deployments list | grep backend-services | grep DONE)")
    return os.environ.get("DEPLOYMENT_COMPLETE")

def break_print(i):
    time.sleep(i)
    print("-----")
    return 0

#Static IP
static_ip = '35.244.246.143'

#check for GCS_BUCKET value
if not os.environ.get("GCS_BUCKET"):
    gcs_bucket = "gcs-to-bq"
else:
    gcs_bucket = os.environ.get("GCS_BUCKET")

# instance template, healthcheck (w/ firewall), MIG, backend service, global lb
# pubsub, bq
os.system("gcloud deployment-manager deployments create backend-services --config=dep-mgr/backend_deployment.yaml")

break_print(2)
print("Deployment completed, starting dataflow streaming job...")

# Start streaming job
deployment_complete = None
os.system("export DEPLOYMENT_COMPLETE=")
while not deployment_complete:
    deployment_complete = check_for_deployment_completion()
os.system("gcloud dataflow jobs run us-pubsub-to-bq --gcs-location gs://dataflow-templates-us-central1/latest/PubSub_to_BigQuery --region us-central1 --max-workers 3 --num-workers 1 --worker-machine-type n1-standard-1 --staging-location gs://{gcs_bucket}/temp/ --subnetwork https://www.googleapis.com/compute/v1/projects/g-grp4-implementation/regions/us-central1/subnetworks/us-subnet-data-analytics --network vpc-global --disable-public-ips --parameters inputTopic=projects/g-grp4-implementation/topics/backend-server-to-bq,outputTableSpec=g-grp4-implementation:pubsub_to_bq.server_data".format(gcs_bucket=gcs_bucket))

break_print(2)
print("Backend services deployment is completed, dataflow streaming job has started...")

break_print(5)
print("The server might take some time to be ready")
break_print(5)
site_up = None
while not site_up:
    os.system("export SITE_UP=$(curl {static_ip} | grep Astray)".format(static_ip=static_ip))
    site_up = os.environ.get("SITE_UP")
    print("The site is not ready yet. Hang tight!")
    time.sleep(20)
now = datetime.datetime.utcnow().strftime('%H:%M:%S')
print("The site is up at {static_ip}! Dataflow Batch Job will now start.".format(static_ip=static_ip))

os.system("gcloud dataflow jobs run us-gcs-to-bq --gcs-location gs://dataflow-templates-us-central1/latest/GCS_Text_to_BigQuery --region us-central1 --max-workers 3 --num-workers 1 --worker-machine-type n1-standard-1 --staging-location gs://{gcs_bucket}/temp --subnetwork https://www.googleapis.com/compute/v1/projects/g-grp4-implementation/regions/us-central1/subnetworks/us-subnet-data-analytics --network vpc-global --disable-public-ips --parameters javascriptTextTransformGcsPath=gs://{gcs_bucket}/dataflow_scripts/transform.js,JSONPath=gs://{gcs_bucket}/dataflow_scripts/bq-schema.json,javascriptTextTransformFunctionName=transform,outputTable=g-grp4-implementation:gcs_to_bq.user_files,inputFilePattern=gs://{gcs_bucket}/*.txt,bigQueryLoadingTemporaryDirectory=gs://{gcs_bucket}/temp".format(gcs_bucket=gcs_bucket))
break_print(2)
print("All test components have completed.")
time.sleep(1)
print("Open README.txt to see EXPECTED RESULTS in various sinks, with GMT_time (approx.): {now}".format(now=now))
break_print(5)
print("This demo is completed, run 'python end_deployment.py' to delete all the resources.")