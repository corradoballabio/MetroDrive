# -*- coding: utf-8 -*-
from viaggio import Viaggio
from processing import analyze,readViaggiTxt
import pymongo
import mysql.connector
import datetime
import json
from bson.objectid import ObjectId

def processFromTxt():
	viaggi = readViaggiTxt("input/badTrip.txt",False)
	viaggio = viaggi[0]
	#viaggio.punti = viaggio.punti[:50]
	distTot, speedingDistance, viaggio = analyze(viaggio)
	viaggio.printPunti()

def main():
	cont = True
	while cont:
		ret = process()
		if ret != None: cont = False

def process():
	collection = connectToMongo()
	viaggio = getFromMongo(collection)
	if viaggio!=None:
		tupla = analyze(viaggio)
		if isinstance(tupla,tuple):
			distTot = tupla[0]
			speedingDistance = tupla[1]
			viaggio = tupla[2]
			#viaggio.printPunti()
			#print viaggio
			if speedingDistance<0:
				print "viaggio",viaggio.id_,"ha ritornato una distanza sopra i limiti negativa"
				collection.update({"_id" : viaggio.id_}, {"$set" :{"processato":"ERROR"}},upsert=False)
			else:
				success = setProcessedMongo(viaggio,collection,speedingDistance,distTot)
			print ""
		else:
			collection.update({"_id" : viaggio.id_}, {"$set" :{"processato":"ERROR"}},upsert=False)
			print u"Si è verificato un errore durante l'estrazione degli indici."
	else: return False

def connectToMongo():
	try:
		client = pymongo.MongoClient('127.0.0.1', 27017)
		db = client.metrodrive
		collection = db.viaggi
		return collection
	except pymongo.errors.ServerSelectionTimeoutError as e:
		print e
		print "Il database Mongodb non può essere raggiunto"

def setProcessedMongo(viaggio, collection, speedingDistance, distTot):
	viaggio = viaggio.toJSON()
	viaggio = json.loads(viaggio)
	punti = viaggio["punti"]
	res = collection.update({"_id" : ObjectId(viaggio["id"])}, {'$set':{"processato":"YES", "punti" : punti, "speedingDist" : speedingDistance, "distTot" : distTot}},upsert=False)
	if res["updatedExisting"]==True:
		print u"Estrazione degli indici completata e viaggio analizzato aggiornato su mongoDB"
		return 0
	else:
		return -1

def getFromMongo(collection):
	res = collection.find({"ricevuto" : "YES","processato":"NO"}).sort("tempo_inizio",pymongo.ASCENDING).limit(1)
	#res = collection.find({"_id": ObjectId("593e55797dbeeb0cc808f8e2")})
	doc = next(res, None)
	if doc:
		res = collection.update({"_id" : doc["_id"]}, {"$set":{"processato":"PROCESSING"}},upsert=False)
		v = Viaggio(0,0,0,[])
		v.fromJSON(doc)
		#v.punti = v.punti[:30] ###
		return v
	else:
		print u"Non sono stati trovato viaggi da processare."

def connectToSQL():
    """ Connect to MySQL database """
    try:
        conn = mysql.connector.connect(host='192.168.0.100',
                                       database='metrodrivedb',
                                       user='root',
                                       password='11cr+bl12!')
        if conn.is_connected():
            print('Connessione a database MySQL stabilita.')
            return conn
        else:
        	print('Connessione a databgase MySQL fallita.')
 
    except mysql.connector.Error as e:
        print(e)

def storeOnSQL():
	conn = connectToSQL()
	query = ("UPDATE Indicediguida SET kmTot = kmtot + %s,kmSopraLimiti = kmSopraLimiti + %s WHERE Dongle_idDongle=%s and data=%s")
	data = (100,50,5000,datetime.date(2016,8,1))
	cursor = conn.cursor()
	cursor.execute(query,data)

	# accept the changes
	conn.commit()

if __name__ == '__main__':
	main()
