# -*- coding: utf-8 -*-
from datetime import datetime
from punto import Punto

class Viaggio:
    def __init__(self, id_, tstart, tend, punti_list):
        self.id_ = id_
        self.tempo_inizio = tstart
        self.tempo_fine = tend
        self.punti = punti_list
    
    # def __init__(self):
    #     self.id_ = ""
    #     self.tempo_inizio = ""
    #     self.tempo_fine = ""
    #     self.punti = []

    def fromJSON(self,json):
    	self.id_ = json["_id"]
        self.tempo_inizio = json["tempo_inizio"]
        self.tempo_fine = "0"
        for punto in json["punti"]:
        	p = Punto(0,0,0,0)
        	p.fromJSON(punto)
        	self.punti.append(p)
    
    def toJSON(self):
    	idp = "\"id\" : \""+str(self.id_)+"\""
    	tinizio = "\"tempo_inizio\" : \""+str(self.tempo_inizio)+"\""
    	tfine = "\"tempo_fine\" : \""+str(self.tempo_fine)+"\""
    	punti = "\"punti\" : ["
    	for punto in self.punti:
    		punti = punti + punto.toJSON() + ","
    	punti = punti[0:punti.rfind(",")] + "]"
    	return str("{ "+idp+", "+tinizio+", "+tfine+", "+punti+" }")

    def __str__(self):
	    return "Id viaggio:\t"+str(self.id_)+"\nInizio:\t\t"+str(self.tempo_inizio)+"\nFine:\t\t"+str(self.tempo_fine)+"\nNumero punti:\t"+str(len(self.punti))

    def printPunti(self):
    	for punto in self.punti:
    		print punto,"\n"

    def setDistances(self,distances):
    	numPunti = len(self.punti)
    	if len(distances)!=numPunti:
    		print "num punti != num distanze: ",numPunti,"!=",len(distances)
    	else:
    		i = 0
    		while i<numPunti:
    			self.punti[i].setDistance(distances[i])
    			i = i+1    

    def setMaxSpeeds(self,speeds):
    	numPunti = len(self.punti)
    	if len(speeds)!=numPunti:
    		print "num punti != num velocità"
    	else:
    		i = 0
    		while i<numPunti:
    			self.punti[i].setMaxSpeed(speeds[i])
    			i = i+1

    def addPoint(self, punto):
        self.punti.append(punto)
        
    def get_start_data(self):
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        ret = datetime.strptime(self.tempo_inizio,fmt)
        return ret
        
    def get_end_data(self):
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        ret = datetime.strptime(self.tempo_fine,fmt)
        return ret
        
    def get_punti(self):
        return self.punti

    def getCoords(self):
        coords = []
        for punto in self.punti:
            coords.append(str(punto.latitudine)+","+str(punto.longitudine))
        return coords

    def getCoordsOsrm(self):
        coords = self.getCoords()
        return self.toOsrmFormat(coords)

    def toOsrmFormat(self,coords):
        #Le api OSM utilizzano coordinate in formato Longitudine, Latitudine, sottoforma di tupla di float
        swappedCoords = []
        for coord in coords:
            coord = coord.split(",")
            swappedCoords.append((float(coord[1]),float(coord[0]))) 
        return swappedCoords

    def removeClosePoints(self):
    	i = 1
    	while i<len(self.punti):
    		if self.punti[i].distance <= 0: self.punti.remove(self.punti[i])
    		i = i +1