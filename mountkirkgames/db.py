import requests, json, os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import pubsub_v1

# Use the application default credentials
cred = credentials.ApplicationDefault()
project_id = os.environ.get('DEVSHELL_PROJECT_ID')
firebase_admin.initialize_app(cred, {
  'projectId': projectid,
})

db = firestore.client()

response = requests.get("https://ipgeolocation.abstractapi.com/v1/?api_key=7cd29c75593445baa0ae7068c297c1bc")
response = json.loads(response.content.decode("utf-8"))

hour = int(response['timezone']['current_time'][0:2]) - response['timezone']['gmt_offset']

if hour < 0:
  hour = 24 + hour
elif hour > 24:
  hour = 0 + hour - 24

time = str(hour) + response['timezone']['current_time'][2:]

# inserting into firestore
doc_ref = db.collection(u'users').document(response['country_code'] + " @ " + time + " GMT")
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