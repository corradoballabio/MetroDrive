# -*- coding: utf-8 -*-
from viaggio import Viaggio
from processing import analyze
from collector import json_txt_to_viaggi
import pymongo
from pprint import pprint

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client.metrodrive
collection = db.viaggi

#viaggi = json_txt_to_viaggi("input/2131428.txt")
#distTot, speedingDistance, viaggio = analyze(viaggi[5])
#v = ast.literal_eval(viaggio.toJSON())
#v = { "id" : "21314285", "tempo_inizio" : "2012-03-03T10:00:26Z", "tempo_fine" : "2012-03-03T10:04:10Z", "punti" : [{ "timestamp" : "2012-03-03T10:00:26Z", "lat" : "45.414579", "lon" : "10.509934", "vel" : "9", "maxvel" : "90", "dist" : "0" },{ "timestamp" : "2012-03-03T10:00:32Z", "lat" : "45.414194", "lon" : "10.509812", "vel" : "39", "maxvel" : "90", "dist" : "43" },{ "timestamp" : "2012-03-03T10:00:34Z", "lat" : "45.413973", "lon" : "10.509741", "vel" : "49", "maxvel" : "90", "dist" : "25" },{ "timestamp" : "2012-03-03T10:00:43Z", "lat" : "45.412651", "lon" : "10.509259", "vel" : "69", "maxvel" : "90", "dist" : "151" },{ "timestamp" : "2012-03-03T10:00:54Z", "lat" : "45.410752", "lon" : "10.508988", "vel" : "64", "maxvel" : "90", "dist" : "212" },{ "timestamp" : "2012-03-03T10:01:06Z", "lat" : "45.408750", "lon" : "10.509556", "vel" : "69", "maxvel" : "90", "dist" : "226" },{ "timestamp" : "2012-03-03T10:01:17Z", "lat" : "45.406884", "lon" : "10.509736", "vel" : "69", "maxvel" : "90", "dist" : "211" },{ "timestamp" : "2012-03-03T10:01:27Z", "lat" : "45.405231", "lon" : "10.508836", "vel" : "69", "maxvel" : "90", "dist" : "197" },{ "timestamp" : "2012-03-03T10:01:35Z", "lat" : "45.404050", "lon" : "10.507738", "vel" : "69", "maxvel" : "90", "dist" : "159" },{ "timestamp" : "2012-03-03T10:01:51Z", "lat" : "45.402118", "lon" : "10.504727", "vel" : "69", "maxvel" : "90", "dist" : "318" },{ "timestamp" : "2012-03-03T10:02:05Z", "lat" : "45.400145", "lon" : "10.502554", "vel" : "69", "maxvel" : "90", "dist" : "277" },{ "timestamp" : "2012-03-03T10:02:33Z", "lat" : "45.396150", "lon" : "10.498354", "vel" : "74", "maxvel" : "90", "dist" : "552" },{ "timestamp" : "2012-03-03T10:02:41Z", "lat" : "45.394881", "lon" : "10.497562", "vel" : "69", "maxvel" : "90", "dist" : "154" },{ "timestamp" : "2012-03-03T10:02:55Z", "lat" : "45.392543", "lon" : "10.496742", "vel" : "69", "maxvel" : "90", "dist" : "269" },{ "timestamp" : "2012-03-03T10:03:02Z", "lat" : "45.391643", "lon" : "10.496719", "vel" : "44", "maxvel" : "90", "dist" : "100" },{ "timestamp" : "2012-03-03T10:03:17Z", "lat" : "45.390027", "lon" : "10.496294", "vel" : "49", "maxvel" : "90", "dist" : "186" },{ "timestamp" : "2012-03-03T10:03:27Z", "lat" : "45.389172", "lon" : "10.495374", "vel" : "39", "maxvel" : "90", "dist" : "121" },{ "timestamp" : "2012-03-03T10:03:36Z", "lat" : "45.388309", "lon" : "10.494402", "vel" : "49", "maxvel" : "90", "dist" : "122" },{ "timestamp" : "2012-03-03T10:03:41Z", "lat" : "45.387926", "lon" : "10.493974", "vel" : "19", "maxvel" : "90", "dist" : "54" },{ "timestamp" : "2012-03-03T10:03:46Z", "lat" : "45.387813", "lon" : "10.493861", "vel" : "14", "maxvel" : "90", "dist" : "15" },{ "timestamp" : "2012-03-03T10:03:47Z", "lat" : "45.387785", "lon" : "10.493833", "vel" : "19", "maxvel" : "90", "dist" : "3" },{ "timestamp" : "2012-03-03T10:03:48Z", "lat" : "45.387835", "lon" : "10.493505", "vel" : "24", "maxvel" : "50", "dist" : "31" },{ "timestamp" : "2012-03-03T10:03:49Z", "lat" : "45.387739", "lon" : "10.493787", "vel" : "29", "maxvel" : "90", "dist" : "23" },{ "timestamp" : "2012-03-03T10:03:50Z", "lat" : "45.387991", "lon" : "10.493539", "vel" : "29", "maxvel" : "90", "dist" : "216" },{ "timestamp" : "2012-03-03T10:03:51Z", "lat" : "45.387998", "lon" : "10.493531", "vel" : "34", "maxvel" : "90", "dist" : "187" },{ "timestamp" : "2012-03-03T10:03:52Z", "lat" : "45.387961", "lon" : "10.493127", "vel" : "34", "maxvel" : "50", "dist" : "28" },{ "timestamp" : "2012-03-03T10:03:53Z", "lat" : "45.388000", "lon" : "10.493010", "vel" : "34", "maxvel" : "50", "dist" : "10" },{ "timestamp" : "2012-03-03T10:04:04Z", "lat" : "45.388354", "lon" : "10.491981", "vel" : "9", "maxvel" : "50", "dist" : "89" },{ "timestamp" : "2012-03-03T10:04:10Z", "lat" : "45.388370", "lon" : "10.491936", "vel" : "4", "maxvel" : "50", "dist" : "3" }] }
res = collection.find({"ricevuto" : "YES","processato":"NO"}).sort("tempo_inizio",pymongo.ASCENDING).limit(1)
doc = res[0]
res = collection.update({"_id" : doc["_id"]}, {"processato":"PROCESSING"},upsert=False)
v = Viaggio()
v.fromJSON(doc)
#res = collection.update({"_id" : doc["_id"]}, {"processato":"YES"},upsert=False)
#print res
#distTot, speedingDistance, v = analyze(v)
print v
v.printPunti()
#print distTot, speedingDistance
#collection.insert_one({"altro oggetto fittizio"	: "altro campo fittizio"})