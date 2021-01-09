
from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

@app.route("/")
def default():
    os.system('python /var/www/mountkirkgames/mountkirkgames/db.py')
    return render_template("index.html")
    
@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)
if __name__ == "__main__":
    app.run()