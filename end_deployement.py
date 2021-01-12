import os
import time

os.system("gcloud dataflow jobs cancel $(gcloud dataflow jobs list | grep Running | awk '($1) {print $1}') --region=us-central1")
print("Dataflow streaming job ended.")

time.sleep(2)
os.system("gcloud deployment-manager deployments delete backend-services --quiet")
print("Resources have been deleted. Have a good day!")