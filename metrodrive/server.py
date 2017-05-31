from flask import Flask, request, session, json
from pymongo import MongoClient
import pprint, os

#export FLASK_APP=hello.py
#export FLASK_DEBUG=1
#flask run

app = Flask(__name__)
app.secret_key = os.urandom(24)
mongo_client = MongoClient('localhost', 27017)
db = mongo_client.metrodrive
viaggi = db.viaggi

@app.route("/metrodrive/api/v0.1/login", methods=["POST"])
def login():
    session['username'] = request.data
    print str(request['device_id']) + " logged."
    
@app.route("/metrodrive/api/v0.1/logout")
def logout():
    username = session['username']
    session.pop('username', None)
    print  username + "logged out."

@app.route("/metrodrive/api/v0.1/data", methods=['POST'])
def api_send_data():
    if 'username' not in session:
        return "Not logged", 401 
    if request.headers['Content-Type'] == "application/json":
        
        jreq = request.json
        post = viaggi.find_one({"viaggio_id": jreq['viaggio_id'], "device_id": jreq["device_id"]})
        if post is not None:
            #aggiungi a post del viaggio
            post["punti"] = post["punti"] + jreq["punti"]
            viaggi.save(post)
            print "aggiornato post in viaggio"
        else:
            #crea nuovo post
            post_id = viaggi.insert_one(request.json).inserted_id
            print "aggiunto nuovo post in viaggio"
    
        return "OK", 200
    else:
        return "Unsupported Media Type", 415
    
@app.route("/metrodrive/hello")
def hello_world():
    return "Hello, I'm Flask."

if __name__ == '__main__':
    viaggi.delete_many({}) #svuota db
    app.run(debug = True)