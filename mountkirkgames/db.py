import requests, json, os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import pubsub_v1
from google.cloud import storage
from datetime import datetime

dt = datetime.utcnow().strftime("%Y-%m-%d, %H:%M:%S")
time = datetime.utcnow().strftime("%H:%M:%S")

# Use the application default credentials
cred = credentials.ApplicationDefault()
project_id = 'g-grp4-implmentation'
firebase_admin.initialize_app(cred, {
  'projectId': project_id,
})

db = firestore.client()

response = requests.get("https://ipgeolocation.abstractapi.com/v1/?api_key=7cd29c75593445baa0ae7068c297c1bc")
response = json.loads(response.content.decode("utf-8"))

# inserting into firestore
doc_ref = db.collection(u'users').document(response['country_code'] + " @ " + dt + " GMT")
doc_ref.set(response)

#inserting into pubsub topic "backend-server-to-bq"
publisher = pubsub_v1.PublisherClient()
topic_id = "backend-server-to-bq"
topic_path = publisher.topic_path(project_id, topic_id)
message = {
  "ip_address": response['ip_address'],
  "longitude": response["longitude"],
  "latitude": response['latitude'],
  "GMT_time": time
}
future = publisher.publish(topic_path, json.dumps(message).encode("utf-8"))

#inserting data into GCS
from_vm = response["city"] + "," + response["ip_address"] + "," + time + "," + "reset password (test from backend)"

storage_client = storage.Client()
bucket_name = "gcs-to-bq"
bucket = storage_client.bucket(bucket_name)
destination_blob_name = "from_vm.txt"
blob = bucket.blob(destination_blob_name)
blob.upload_from_string(from_vm)