from flask import Flask, request, session, json
from pymongo import MongoClient
from bson import ObjectId
import pprint, os
from OpenSSL import SSL
from cryptography.fernet import Fernet

#export FLASK_APP=hello.py
#export FLASK_DEBUG=1
#flask run

#TODOS:
# - prendere solo viaggi italia
# - mettere nelle sessioni id_device e id_viaggio
# - salvare in modo univoco id viaggio
# - aggiungere flag ricezione e processing

app = Flask(__name__)
mongo_client = MongoClient('localhost', 27017)
db = mongo_client.metrodrive
viaggi = db.viaggi
devices = db.devices

def setup_db():
    viaggi.delete_many({}) #svuota db
    devices.delete_many({})
    f = open("keys", "r")
    for l in f.readlines()[1:]:
        ls = l.split("\t")
        (device_id, shared_pwd) = ls[0], ls[1].rstrip()
        devices.insert_one({"device_id":device_id,"shared_key":shared_pwd})
        
def decode(did, payload):
    post = devices.find_one({"device_id": did})
    if post is not None:
        shared_key = post["shared_key"].encode('utf-8')
        cipher_suite = Fernet(shared_key)
        message = cipher_suite.decrypt(bytes(payload))
        return message
    return -1
        
@app.route("/metrodrive/api/v0.1/login", methods=["POST"]) #mettere_username_nell'url
def login():
    jreq = request.json
    device_id = jreq["device_id"]
    post = devices.find_one({"device_id": device_id})
    if post is not None:
        shared_key = post["shared_key"].encode('utf-8')
        cipher_suite = Fernet(shared_key)
        if jreq["device_id"] == cipher_suite.decrypt(bytes(jreq["signature"])):
            session['device_id'] = jreq["device_id"]
            print session['device_id'] + " logged."
            return "OK", 200
    print "Login attempt failed."
    return "Login error", 401
    
@app.route("/metrodrive/api/v0.1/logout", methods=["GET"])
def logout():
    if 'viaggio_id' not in session:
        "Logout error: device not logged.", 401
    device_id = session['device_id']
    session.pop('device_id', None)
    session.pop('viaggio_id', None)
    print  device_id + " logged out."
    return "OK", 200

@app.route("/metrodrive/api/v0.1/data", methods=['POST'])
def api_send_data():
    print len(session.keys())
    
    if 'device_id' not in session:
        return "Device not logged.", 401 
        
    #invia json come testo cifrato 
    if request.headers['Content-Type'] == "application/text":
        
        ddata = decode(session['device_id'], request.data)
        jdata = json.loads(ddata)
        
        if 'viaggio_id' not in session:
            
            #crea nuovo post
            jviaggio = {"device_id": session["device_id"], "ricevuto": False, "processato": False,
                         "tempo_inizio" : jdata["tempo_inizio"], "punti" : jdata["punti"] }
                         
            viaggio_id = viaggi.insert_one(jviaggio).inserted_id
            session["viaggio_id"] = str(viaggio_id)
            print "Aggiunto nuovo viaggio " + session["viaggio_id"]
        else:
            print session["viaggio_id"]
            post = viaggi.find_one({"_id": ObjectId(session["viaggio_id"])})
            #aggiungi a post del viaggio
            post["punti"] = post["punti"] + jdata["punti"]
            viaggi.save(post)
            print "Aggiunti punti in viaggio " + session["viaggio_id"]
            
        return "OK", 200
        
    #invia json come testo *non* cifrato 
    elif request.headers['Content-Type'] == "application/json":
        
        jdata = request.json
        
        if 'viaggio_id' not in session:
            
            #crea nuovo post
            jviaggio = {"device_id": session["device_id"], "ricevuto": False, "processato": False,
                         "tempo_inizio" : jdata["tempo_inizio"], "punti" : jdata["punti"] }
                         
            viaggio_id = viaggi.insert_one(jviaggio).inserted_id
            session["viaggio_id"] = str(viaggio_id)
            print "Aggiunto nuovo viaggio " + session["viaggio_id"]
        else:
            print session["viaggio_id"]
            post = viaggi.find_one({"_id": ObjectId(session["viaggio_id"])})
            #aggiungi a post del viaggio
            post["punti"] = post["punti"] + jdata["punti"]
            viaggi.save(post)
            print "Aggiunti punti in viaggio " + session["viaggio_id"]
            
        return "OK", 200
    else:
        return "Unsupported Media Type", 415
    
@app.route("/metrodrive/hello")
def hello_world():
    return "Hello, I'm Flask."

if __name__ == '__main__':
    setup_db()
    app.secret_key = os.urandom(24)
    app.run(host='127.0.0.1', port=5000, debug = True)