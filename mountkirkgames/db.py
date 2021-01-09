import requests, json, os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use the application default credentials
cred = credentials.ApplicationDefault()
projectid = os.environ.get('DEVSHELL_PROJECT_ID')
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


doc_ref = db.collection(u'users').document(response['country_code'] + " @GMT " + time)
doc_ref.set(response)