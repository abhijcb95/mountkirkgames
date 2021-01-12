MOUNTKIRK GAMES Implementation

# This file is to explain how to deploy all the necessary resources for mountkirkgames #

----- RESOURCES TO BE DEPLOYED:
- A single global network communicating via internal IP address, with firewalls and NAT configured to serve external requests
- A global gaming server setup with at least 1 running server in US, EU and Asia all the time
- Serverless, scalable NoSQL database useful for storing and retrieving game states rapidly
- Streamed data from game servers through an ETL pipeline into a data warehouse, fully serverless and highly scalable
- Files uploaded to a serverless blob storage can be processed in batched jobs that can be triggered manually, scheduled or by events

----- EXPECTED RESULTS: (after completing QUICK/FULL DEPLOYMENT)
- Check Firestore 'users' collection for an entry indicating the GMT_time your request was served
- Check Bigquery 'gcs_to_bq' dataset, 'user_files' table preview for 2 entries- (1 test and 1 from the your request)
- Check Bigquery 'pubsub_to_bq' dataset, 'server_data' table preview for 1 entry indicating with the GMT_time of your request

## DISCLAIMER: Bigquery might take some time to receive the data

## Code to run batch job: 
gcloud dataflow jobs run us-gcs-to-bq --gcs-location gs://dataflow-templates-us-central1/latest/GCS_Text_to_BigQuery --region us-central1 --max-workers 3 --num-workers 1 --worker-machine-type n1-standard-1 --staging-location gs://gcs-to-bq/temp --subnetwork https://www.googleapis.com/compute/v1/projects/g-grp4-implementation/regions/us-central1/subnetworks/us-subnet-data-analytics --network vpc-global --disable-public-ips --parameters javascriptTextTransformGcsPath=gs://gcs-to-bq/dataflow_scripts/transform.js,JSONPath=gs://gcs-to-bq/dataflow_scripts/bq-schema.json,javascriptTextTransformFunctionName=transform,outputTable=g-grp4-implementation:gcs_to_bq.user_files,inputFilePattern=gs://gcs-to-bq/*.txt,bigQueryLoadingTemporaryDirectory=gs://gcs-to-bq/temp

## remember to run 'python delete_deployment.py' after seeing results to prevent incurring unnecessary costs.

----- QUICK DEPLOYMENT: (for use in g-group-4 project; PRE-REQUISITES COMPLETED)
git clone https://github.com/abhijcb95/mountkirkgames.git
cd mountkirkgames
python deployment.py

# check for expected results
run 'python delete_deployment.py'
----- (for use in new project, refer to FULL DEPLOYMENT below)

---- CONGRATULATIONS ----
You have reached the end of this demo!
# All inputs come from VM and can be changed according to application requirements.

Hope you enjoyed this demonstration. Thank you very much.
--------------------------------------

----- FULL DEPLOYMENT (for use in new project; PRE-REQUISITES NOT COMPLETED)
# PRE-REQUISITES
1. git clone https://github.com/abhijcb95/mountkirkgames.git
2. cd mountkirkgames
3. run 'gcloud deployment-manager deployments create networks --config=network.yaml'
4. set up cloud NAT & router for us-central1, europe-west6, asia-east2
5. firestore must be set up with 'users' collection
6. reserve Static GLOBAL external ip_address
7. create service account with read/write to GCS, Firestore and Pubsub, email_id: service-account-backend-server@...
8. read 'new_deployment/create_golden_image.txt' to create base vm (stop running after completed)
9. create golden image named 'image-backend-server' to create instance templates in deployment later
10. create gcs bucket, run 'python new_deployment/new_gcs-to-bq.py', change gcs sinks for dataflow jobs in 'deployment.py'

# PRE-REQUISITES COMPLETED
11. run 'python deployment.py'
12. check for expected results
13. run 'python delete_deployment.py'
