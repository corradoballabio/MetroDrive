# -*- coding: utf-8 -*-
import math
import sys
import overpass
import osrm
osrm.RequestConfig.host = "localhost:5000"

from viaggio import Viaggio
from punto import Punto

def main():
    from collector import json_txt_to_viaggi
    #"input/2015075.txt", problematico, l'ultimo pacchetto di distanze arriva con dei None mancanti
    viaggi = json_txt_to_viaggi("input/2131428.txt")
    i = 0
    for viaggio in viaggi:
        #print "Viaggio",i,"composto da",len(viaggio.punti),"punti."
        i = i + 1

    viaggio = viaggi[15]
    #viaggio.punti = viaggio.punti[:30]
    distTot, speedingDistance = analyze(viaggio)
    print "Distanza totale:",int(distTot),"m"
    print "Distanza sopra i limiti:",speedingDistance,"m"

def analyze(viaggio):
    print "Viaggio composto da",len(viaggio.punti),"punti."
    
    speeds = getMaxSpeeds(viaggio,False)
    viaggio.setMaxSpeeds(speeds)
    
    distTot, distances = getDistances(viaggio,False)
    viaggio.setDistances(distances)
    speedingDistance = getSpeedingDistance(viaggio)

    return distTot, speedingDistance

def getSpeedingDistance(viaggio):
    punti = viaggio.get_punti()
    npunti = len(punti)
    i = 0
    km_up = 0
    lastperc = 0                                                                                                #
    while i<npunti-1:
        perc = int(float(i+1)/(npunti-1)*100)                                                                   #
        if lastperc!=perc:                                                                                      #
            print "Calcolo distanza sopra i limiti:",perc,"%\r",                                                #
            sys.stdout.flush()                                                                                  #
        lastperc = perc                                                                                         #
        p1 = punti[i]
        p2 = punti[i+1]
        lim1 = p1.maxspeed
        lim2 = p2.maxspeed
        v1 = p1.velocita
        v2 = p2.velocita
        i = i+1
        if v1 <= lim1 and v2 <= lim2:
            continue
        elif v1 > lim1 and v2 > lim2:
            # km tra p1 e p2
            km_up += p2.distance
        elif v1 > lim1 and v2 <= lim2:
            #print p1,p2,"\n"
            div = (p2.velocita - p1.velocita)
            if div == 0: div = 1
            x = (((lim1 - p1.velocita)*(p2.distance))/div)#+p1["km"]
            km_up += x
        elif v1 <= lim1 and v2 > lim2:
            #print p1,p2,"\n"
            div = (p2.velocita - p1.velocita)
            if div == 0: div = 1
            x = (((lim1 - p1.velocita)*(p2.distance))/div)#+p1["km"]
            km_up += p2.distance - x
    print ""                                                                                                     #
    return km_up

def getDistances(viaggio,verbose):
    blocksize = 99
    distances = [0]
    steps = []
    tracepoints = []
    totalDistance = 0
    coords = viaggio.getCoordsOsrm()

    nblocks = math.floor(float(len(coords)-1)/blocksize)
    k = 0
    lastperc = 0                                                                                                #
    while k<=nblocks:
        perc = int(float(k+1)/(nblocks+1)*100)                                                                  #
        block = []
        if lastperc!=perc:                                                                                      #
            print "Ottengo distanze tra i punti:",perc,"%\r",                                                   #
            sys.stdout.flush()                                                                                  #
        lastperc = perc                                                                                         #
        if k==0:
            block = coords[k*blocksize:(k+1)*blocksize]
            #print "Indici blocco:",k*blocksize,(k+1)*blocksize-1,"dim blocco =",len(block)
        elif k <nblocks:
            block = coords[k*blocksize-1:(k+1)*blocksize]
            #print "Indici blocco:",k*blocksize-1,(k+1)*blocksize-1,"dim blocco =",len(block)
        elif k==nblocks:
            block = coords[k*blocksize-1:]
            #print "Indici blocco:",k*blocksize-1,len(coords)-1,"dim blocco =",len(block)
        
        if len(block)>1:
            result = osrm.match(block)
            totalDistance = totalDistance + (result["matchings"][0]["distance"])
            
            tempSteps = result["matchings"][0]["legs"]
            steps.extend(tempSteps)
            tempTraces = result["tracepoints"]
            tempTraces.pop(0) #RIMUOVE LA PRIMA TRACCIA POICHE' SI RIFERISCE A UNA DISTANZA GIA' CONTATA
            tracepoints.extend(tempTraces)
        # else:
        #     print "Sono in un ramo dove non dovrei mai entrare"
            
        k = k+1
    print ""                                                                                                     #

    for tracepoint in tracepoints:
        if tracepoint == None:
            distances.append(-4)
        else:
            if len(steps)>0:
                distances.append(steps.pop(0)["distance"])
            else:
                distances.append(-5)

    if verbose: print "Lunghezza array distanze:",str(len(distances))
    return totalDistance,distances

def getMaxSpeeds(viaggio,verbose):
    coords = viaggio.getCoords()
    maxspeeds = []
    ncoords = len(coords)
    i=0
    lastperc = 0                                                #
    while i<ncoords:
        perc = int(float(i+1)/(ncoords)*100)                    #
        if lastperc!=perc:                                      #
            print "Ottengo velocità massime:",perc,"%\r",       #
            sys.stdout.flush()                                  #
        tmp = getMaxspeed(coords[i],verbose)
        maxspeeds.append(tmp)
        i = i + 1
        lastperc = perc                                         #
    print ""                                                    #
    #print "Lunghezza array velocità:",str(len(maxspeeds))
    maxspeeds = fixSpeeds(maxspeeds)
    return maxspeeds

def getMaxspeed(coord,verbose):
    api = overpass.API(endpoint="http://localhost/api/interpreter")
    query = '(around:10,%s)' % (coord)
    way_query = overpass.WayQuery(query)
    response = api.Get(way_query)
    results = response["features"]
    roads = []
    
    #primo filtraggio: per ogni coordinata assegno una o più strade, eliminando tutto il resto
    for result in results:
        if result["properties"]:
            result = result["properties"]
            if "highway" in result:
                if "motorway" in result["highway"]: roads.append(result)
                if "trunk" in result["highway"]: roads.append(result)
                if "primary" in result["highway"]: roads.append(result)
                if "secondary" in result["highway"]: roads.append(result)
                if "tertiary" in result["highway"]: roads.append(result)
                if "unclassified" in result["highway"]: roads.append(result)
                if "residential" in result["highway"]: roads.append(result)
                
    #se l'array roads non contiene nessuna strada allora non è stata trovata nessuna strada
    if len(roads)==0:
        if verbose: print "Strada non trovata"
        return -2        
    
    #se più di una strada passa il filtraggio, bisogna tenere la più significativa 
    if len(roads)>1:
        mask = []
        for road in roads:
            if "maxspeed" in road: mask.append(road)
        #if len(mask)>1 : print "PIU' DI UNA STRADA SOPRAAVVISSUTA AL FILTRAGGIO"#, results
        roads = mask        
    
    
    if len(roads)>0:
        #a questo punto dovrebbe esserci solo un elento all'interno dell'array
        road = roads[0]
        roadmaxspeeds = []
        for road in roads:
            maxspeed = 0
            
            #se c'è il tag "maxspeed" allora prendo direttamente quel valore
            if "maxspeed" in road:
                maxspeed = int(road["maxspeed"])
        
            #se il tipo di "highway" è "residential" o "motorway" allora non serve differenziare tra strada urbana o interurbana
            if maxspeed==0:
                if "residential" in road["highway"]:
                    maxspeed = 50
                if "trunk" in road["highway"]:
                    maxspeed = 90
                if "motorway" in road["highway"]:
                    maxspeed = 130
            
            #se gli if precedenti falliscono allora controllo se la strada è urbana o interurbana (tramite presenza o meno del marciapiede) e poi controllo il tipo di strada (primary, secondary,tertiary o unclassified)
            if maxspeed==0:
                speeds = {
                        "urban" : {"primary" : 50, "secondary" : 50, "tertiary" : 50, "unclassified" : 50}, 
                        "interurban" : {"primary" : 90, "secondary" : 90, "tertiary" : 90, "unclassified" : 70}
                          }
                type = None
                if "sidewalk" in road: type="urban"
                else: type="interurban"
                maxspeed = speeds[type][road["highway"]]
            
            #se nessuno dei filtraggi precedenti trovasse la velocità massima, segnalo il fallimento della ricerca della velocità massima
            if maxspeed==0:
                maxspeed = -1    
        
            roadmaxspeeds.append(maxspeed)

        return max(roadmaxspeeds)
    
    else:
        if verbose: print "Velocità massima non trovata."
        return -1

def fixSpeeds(speeds):
    npunti = len(speeds)
    if speeds[0]<0:
        i = 1
        while i<npunti:
            if speeds[i]<0:
                i = i+1
            else:
                speeds[0] = speeds[i]
                i = npunti
    i=0
    while i<npunti:
        if speeds[i] < 0:
            if i==0: speeds[i] = speeds[i+1]
            if i>0 and i<npunti-1:
                if speeds[i-1] > 0 and speeds[i+1] < 0: speeds[i] = speeds[i-1]
                if speeds[i-1] < 0 and speeds[i+1] > 0: speeds[i] = speeds[i+1]
                if speeds[i-1] > 0 and speeds[i+1] > 0: speeds[i] = max(speeds[i-1],speeds[i+1])
            if i==npunti-1: speeds[i] = speeds[i-1] 
        i = i+1
    return speeds
    
def toOsrmFormat(strCoord):
    coord = strCoord.split(",")
    return (float(coord[1]),float(coord[0]))

def get_indici(viaggio):
    pass

def print_viaggi(viaggi):
    i=0
    for viaggio in viaggi:
        print i,"\n",viaggio,"\n"
        i = i+1

if __name__ == '__main__':
    main()  