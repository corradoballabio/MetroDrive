from flask import Flask, request, session, json
from pymongo import MongoClient
from bson import ObjectId
import pprint, os
from cryptography.fernet import Fernet
from datetime import datetime

#export FLASK_APP=hello.py
#export FLASK_DEBUG=1
#flask run

app = Flask(__name__)
mongo_client = MongoClient('localhost', 27017)
db = mongo_client.metrodrive
viaggi = db.viaggi
devices = db.devices


def fromepoch(date_str):
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    dt = datetime.strptime(date_str,fmt)
    epoch = datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds()


def setup_db():
    """
    Esegue setup del database Mongo: svuota dati preesistenti e inizializza db.devices con
    i dati contenuti nel file "keys".
    """
    viaggi.delete_many({}) 
    devices.delete_many({})
    f = open("keys", "r")
    for l in f.readlines()[1:]:
        ls = l.split("\t")
        (device_id, shared_pwd) = ls[0], ls[1].rstrip()
        devices.insert_one({"device_id":device_id,"shared_key":shared_pwd})
        
def decode(did, payload):
    """
    Decodifica del payload per chiave di cifratura simmetrica condivisa con il client.
    
    :type payload: string
    :param payload: stringa rappresentante i pacchetti cifrati ricevuti dal server
    :rtype: string o None
    :return: il payload decifrato in caso di successo, None in caso contrario
    """
    post = devices.find_one({"device_id": did})
    if post is not None:
        shared_key = post["shared_key"].encode('utf-8')
        cipher_suite = Fernet(shared_key)
        message = cipher_suite.decrypt(bytes(payload))
        return message
    return None
        
@app.route("/metrodrive/api/v0.1/login", methods=["POST"]) 
def login():
    """
    Effettua login sicuro del Client e inizializza sessione di connessione.
    
    :<json string device_id: id del device Client
    :<json string signature: firma digitale, ottenuta tramite cifratura dell'id del device con chiave simmetrica
    :status 200: login effettuato
    :status 401: login fallito
    """
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
    """
    Effettua logout sicuro del Client e termina sessione di connessione.
    
    :status 200: logout effettuato.
    :status 401: logout fallito.
    """
    if 'viaggio_id' not in session:
        "Logout error: device not logged.", 401
    device_id = session['device_id']
    session.pop('device_id', None)
    viaggio_id = session['viaggio_id']
    post = viaggi.find_one({"_id": ObjectId(viaggio_id)})
    post["ricevuto"] = "YES"
    viaggi.save(post)
    session.pop('viaggio_id', None)
    print  device_id + " logged out."
    return "OK", 200

@app.route("/metrodrive/api/v0.1/data", methods=['POST'])
def send_data():
    """
    Riceve dati inviati in modo sicuro dal client relativi ad un viaggio e aggiunge al database.
    
    :reqheader Accept: application/json
    :<json string tempo_inizio: timestamp di inizio del viaggio inviato
    :<json list punti: array di punti in formato json
    
    :reqheader Accept: application/text
    :<text string data: json cifrato con chiave simmetrica, contenente i punti del viaggio inviti
    
    :status 200: ricezione e archiviazione eseguite con successo.
    :status 401: dispositivo non autenticato.
    :status 415: dati di invio non supportati.
    """
    if 'device_id' not in session:
        return "Device not logged.", 401 
    
    #invia json come testo cifrato 
    if request.headers['Content-Type'] == "application/text":
        
        ddata = decode(session['device_id'], request.data)
        jdata = json.loads(ddata)
        
        if 'viaggio_id' not in session:
            
            #crea nuovo post
            jviaggio = {"device_id": session["device_id"], "ricevuto": "NO", "processato": "NO",
                         "tempo_inizio" : fromepoch(jdata["tempo_inizio"]), "punti" : jdata["punti"] }
                         
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
            jviaggio = {"device_id": session["device_id"], "ricevuto": "NO", "processato": "NO",
                         "tempo_inizio" : fromepoch(jdata["tempo_inizio"]), "punti" : jdata["punti"] }
                         
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
    app.run(host='0.0.0.0', port=5000, debug = True)