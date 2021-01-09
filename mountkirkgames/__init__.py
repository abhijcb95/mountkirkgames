
from flask import Flask, render_template, send_from_directory
import requests
import json

app = Flask(__name__)

@app.route("/")
def default():
    response = requests.get("https://ipgeolocation.abstractapi.com/v1/?api_key=7cd29c75593445baa0ae7068c297c1bc")
    response = json.loads(response.content.decode("utf-8"))
    return render_template("index.html")
    
@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)
if __name__ == "__main__":
    app.run()