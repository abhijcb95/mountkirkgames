import os

def check_for_deployment_completion():
    os.system("export DEPLOYMENT_COMPLETE=")
    os.system("export DEPLOYMENT_COMPLETE=$(gcloud deployment-manager deployments list | grep backend-services | grep DONE)")
    DEPLOYMENT_COMPLETE = os.environ.get("DEPLOYMENT_COMPLETE")

    while len(DEPLOYMENT_COMPLETE) == 0:
        os.system("export DEPLOYMENT_COMPLETE=$(gcloud deployment-manager deployments list | grep backend-services | grep DONE)")
        DEPLOYMENT_COMPLETE = os.environ.get("DEPLOYMENT_COMPLETE")

    return True

#check for GCS_BUCKET value
if not os.environ.get("GCS_BUCKET"):
    gcs_bucket = "gcs-to-bq"
else:
    gcs_bucket = os.environ.get("GCS_BUCKET")

# create network, subnets, firewalls
os.system("gcloud deployment-manager deployments create setup --config=dep-mgr/setup_deployment.yaml")

continue_deployment = False
while not continue_deployment:
    print(" 2 Pre-requesites are required here. \n 1. Cloud router and Cloud Nat must be set up for us-central1, europe-west6 and asia-east2. \n 2. A golden image named 'image-backend-server' must be created. \n Type y once completed (ctrl + z to exit deployment)")
    response = input()
    if response == "y":
        continue_deployment = True

print("Setup deployment is completed, deploying the backend services now...")

# instance template, healthcheck (w/ firewall), MIG, backend service, global lb
# pubsub, bq
os.system("gcloud deployment-manager deployments create backend-services --config=dep-mgr/backend_deployment.yaml")

# Start streaming job
deployment_complete = False
while not deployment_complete:
    deployment_complete = check_for_deployment_completion()
os.system("gcloud dataflow jobs run us-pubsub-to-bq --gcs-location gs://dataflow-templates-us-central1/latest/PubSub_to_BigQuery --region us-central1 --max-workers 3 --num-workers 1 --worker-machine-type n1-standard-1 --staging-location gs://{gcs_bucket}/temp/ --subnetwork https://www.googleapis.com/compute/v1/projects/g-grp4-implementation/regions/us-central1/subnetworks/us-subnet-data-analytics --network vpc-global --disable-public-ips --parameters inputTopic=projects/g-grp4-implementation/topics/backend-server-to-bq,outputTableSpec=g-grp4-implementation:pubsub_to_bq.server_data".format(gcs_bucket=gcs_bucket))

print("Backend services deployment is completed, dataflow streaming job has started...")

print("----")
print("The server might take some time to be ready, test it out at 35.244.246.143")
print(" ")
print("After the server is ready and serving the game website, you can test the batch processing job with the following command: ")
print("gcloud dataflow jobs run us-gcs-to-bq --gcs-location gs://dataflow-templates-us-central1/latest/GCS_Text_to_BigQuery --region us-central1 --max-workers 3 --num-workers 1 --worker-machine-type n1-standard-1 --staging-location gs://{gcs_bucket}/temp --subnetwork https://www.googleapis.com/compute/v1/projects/g-grp4-implementation/regions/us-central1/subnetworks/us-subnet-data-analytics --network vpc-global --disable-public-ips --parameters javascriptTextTransformGcsPath=gs://{gcs_bucket}/dataflow_scripts/transform.js,JSONPath=gs://{gcs_bucket}/dataflow_scripts/bq-schema.json,javascriptTextTransformFunctionName=transform,outputTable=g-grp4-implementation:gcs_to_bq.user_files,inputFilePattern=gs://{gcs_bucket}/*.txt,bigQueryLoadingTemporaryDirectory=gs://{gcs_bucket}/temp".format(gcs_bucket=gcs_bucket))
print("----")
print("Open README.txt to see EXPECTED RESULTS in various sinks")
print("----")
print("This demo is completed, run 'python end_deployment.py' to delete all the resources.")