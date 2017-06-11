# -*- coding: utf-8 -*-
import math
import sys
import overpass
import osrm
import urllib2

from viaggio import Viaggio
from punto import Punto

def readViaggiTxt(stringPath,summary):
    '''
    Legge un file txt rappresentate un gruppo di viaggi. Può essere usato 

    :type viaggio: Viaggio
    :param viaggio: L'oggetto Viaggio del quale si vogliono calcolare gli indici
    '''
    from collector import json_txt_to_viaggi
    from os.path import exists
    if exists(stringPath):
        try:
            viaggi = json_txt_to_viaggi(stringPath)
            if summary: print u"Sommario del file",stringPath
            i = 0
            for viaggio in viaggi:
                if summary: print u"Viaggio",i,"composto da",len(viaggio.punti),"punti."
                i = i + 1
            return viaggi
        except IndexError:
            print u"Il file in input non è nel formato previsto."
    else:
        print stringpath,u"is not a valid path."

def analyze(viaggio):
    '''
    Calcola gli indici di un viaggio.

    :type viaggio: Viaggio
    :param viaggio: L'oggetto Viaggio del quale si vogliono calcolare gli indici
    '''
    print u"Viaggio composto da",len(viaggio.punti),"punti."
    
    speeds = getMaxSpeeds(viaggio)
    viaggio.setMaxSpeeds(speeds)
    
    tupla = getDistances(viaggio)
    if isinstance(tupla, tuple):
        distTot = tupla[0]
        distances = tupla[1]
        viaggio.setDistances(distances)
        viaggio.removeClosePoints()
        speedingDistance = getSpeedingDistance(viaggio)
    else:
        return -1

    print u"Distanza totale:",int(distTot),"m"
    print u"Distanza sopra i limiti:",speedingDistance,"m"

    return distTot, speedingDistance, viaggio

def getSpeedingDistance(viaggio):
    '''
    Usa il metodo dell'interpolazione lineare per calcolare quanti metri sopra i limiti di velocità sono stati percorsi durante il viaggio.

    :type viaggio: Viaggio
    :param viaggio: L'oggetto Viaggio del quale si vogliono calcolare i metri percorsi infrangendo i limiti di velocità
    '''
    punti = viaggio.get_punti()
    npunti = len(punti)
    i = 0
    km_up = 0
    speedingPointsCount = 0
    lastperc = 0                                                                                                #
    while i<npunti-1:
        perc = int(float(i+1)/(npunti-1)*100)                                                                   #
        if lastperc!=perc:                                                                                      #
            print u"Calcolo distanza sopra i limiti:",perc,"%\r",                                                #
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
            speedingPointsCount = speedingPointsCount + 1
            x = lineIntersection(p1,p2)
            km_up += x
        elif v1 <= lim1 and v2 > lim2:
            speedingPointsCount = speedingPointsCount + 1
            x = lineIntersection(p1,p2)
            km_up += p2.distance - x
    print ""                                                                                                    #
    print u"Punti sopra il limite di velocità: ",speedingPointsCount
    return int(km_up)

def lineIntersection(p1, p2):
    '''
    A partire da 2 punti crea due rette, una che rappresenta l'andamento della velocità effettiva e una che rappresenta l'andamento della velocità massima.
    Trovando il punto di incontro delle rette, è possibile calcolare quando spazio è stato percorso violando i limiti di velocità.

    :type p1: Punto
    :param p1: il primo Punto

    :type p2: Punto
    :param p2: il secondo Punto
    '''
    s1 = (0,p1.velocita)
    s2 = (p2.distance,p2.velocita)
    l1 = (0,p1.maxspeed)
    l2 = (p2.distance,p1.maxspeed) #
    xdiff = (s1[0]-s2[0],l1[0]-l2[0])
    ydiff = (s1[1]-s2[1],l1[1]-l2[1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(s1,s2), det(l1,l2))
    x = round(float(det(d, xdiff)) / div, 2)
    return x

def chooseBlockSize(viaggio):
    npunti = len(viaggio.punti)
    blocksize = 99 #la massima block size
    if npunti > 99:
        trovato = False
        while not trovato:
            if blocksize > 1:
                if (npunti-blocksize)%(blocksize+1)>1: return blocksize
                else: blocksize = blocksize - 1
            else: raise Error("processing.chooseBlockSize: non ho trovato una blocksize >1")
    else:
        return blocksize

def getDistances(viaggio):
    '''
    Recupera la distanza tra i punti che compongono il viaggio dalla API osrm.

    :type viaggio: Viaggio
    :param viaggio: Il Viaggio del quale si vogliono calcolare le distanze tra punti
    '''
    osrm.RequestConfig.host = "localhost:5000"
    blocksize = chooseBlockSize(viaggio)
    distances = []
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
            print u"Ottengo distanze tra i punti:",perc,"%\r",                                                   #
            sys.stdout.flush()                                                                                  #
        lastperc = perc                                                                                         #
        if k==0:
            block = coords[k*blocksize:(k+1)*blocksize]
        elif k <nblocks:
            block = coords[k*blocksize-1:(k+1)*blocksize]
        elif k==nblocks:
            block = coords[k*blocksize-1:]
        
        if len(block)>1:
            try:
                result = osrm.match(block)
                #if k==0: print result
            except urllib2.HTTPError as e:
                print e
                print u"C'è stato un errore durante il matching dei punti"
                return -1
            
            tempSteps = []
            nmatchings = len(result["matchings"])
            i = 0
            while i<nmatchings:
                totalDistance = totalDistance + (result["matchings"][i]["distance"])
                tempSteps.append({"distance" : 0}) #il primo punto di ogni matching ha distanza dal precedente = 0
                tempSteps.extend(result["matchings"][i]["legs"])
                i = i + 1
            print i

            steps.extend(tempSteps)
            tempTraces = result["tracepoints"]

            nnulltrace = 0
            for trace in tempTraces:
                if trace == None: nnulltrace += 1

            print "Lung. blocco",len(block),"== Lung. traces",len(tempTraces),"?",len(block)==len(tempTraces)
            print "Lung. steps",len(tempSteps),"== Lung. traces",len(tempTraces),"- tracce nulle",nnulltrace,"?",len(tempSteps)==len(tempTraces)-nnulltrace

            if k>0: tempTraces.pop(0) #RIMUOVE LA PRIMA TRACCIA POICHE' SI RIFERISCE A UNA DISTANZA GIA' CONTATA
            tracepoints.extend(tempTraces)



        else:
            print u"processing.getDistances: Non dovresti MAI entrare qui, la tua logica è bacata!"    
        k = k+1
    print ""                                                                                                     #
    nsteps = len(steps)
    nonecount = 0
    for tracepoint in tracepoints:
        if tracepoint == None:
            nonecount = nonecount + 1
            distances.append(-4)
        else:
            if len(steps)>0:
                distances.append(steps.pop(0)["distance"])
            else:
                distances.append(-5)

    print u"npunti:",len(coords),"\nntracepoints:",len(tracepoints),"\nnnone:",nonecount,"\nnsteps:",nsteps
    print distances
    return (totalDistance,distances)

def getMaxSpeeds(viaggio):
    '''
    Per ogni punto che compone il viaggio, recupera dalla API overpass la velocità massima vigente.

    :type viaggio: Viaggio
    :param viaggio: Il Viaggio del quale si vogliono recuperare le velocità massime vigenti sui vari punti 
    '''
    coords = viaggio.getCoords()
    maxspeeds = []
    ncoords = len(coords)
    i=0
    lastperc = 0                                                                                                  #
    while i<ncoords:
        perc = int(float(i+1)/(ncoords)*100)                                                                      #
        if lastperc!=perc:                                                                                        #
            print u"Ottengo velocità massime:",perc,"%\r",                                                         #
            sys.stdout.flush()                                                                                    #
        tmp = getMaxspeed(coords[i])
        maxspeeds.append(tmp)
        i = i + 1
        lastperc = perc                                                                                           #
    print ""                                                                                                      #
    #print "Lunghezza array velocità:",str(len(maxspeeds))
    maxspeeds = fixSpeeds(maxspeeds)
    return maxspeeds

def getMaxspeed(coord):
    '''
    Recupera dalla API overpass la velocità massima vigente in un determinato punto, a partire dalle sue coordinate.

    :type coord: string
    :param coord: le coordinate del punto del quale si vuole scoprire la velocità massima vigente. Le coordinate sono in formato striga "latitudine,longitudine"
    '''
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
        return -2        
    
    #se più di una strada passa il filtraggio, allora provo a filtrarle eliminando quelle non hanno il tag "maxspeed"
    if len(roads)>1:
        mask = []
        for road in roads:
            if "maxspeed" in road: mask.append(road)
        if len(mask)>0: roads = mask                
    
    if len(roads)>0:
        roadmaxspeeds = []
        for road in roads:
            maxspeed = 0
            
            #se c'è il tag "maxspeed" allora prendo direttamente quel valore
            if "maxspeed" in road:
                maxspeed = int(road["maxspeed"])
        
            #se il tipo di "highway" è "residential", "trunk" o "motorway" allora non serve differenziare tra strada urbana o interurbana
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
                if road["highway"]!="primary" and road["highway"]!="secondary" and road["highway"]!="tertiary" and road["highway"]!="unclassified":
                    maxspeed = -1
                else:
                    maxspeed = speeds[type][road["highway"]]
            
            #se nessuno dei filtraggi precedenti trovasse la velocità massima, segnalo il fallimento della ricerca della velocità massima
            if maxspeed==0:
                maxspeed = -1    
        
            roadmaxspeeds.append(maxspeed)

        return max(roadmaxspeeds)
    
    else:
        return -1 #velocità massima non trovata

def fixSpeeds(speeds):
    '''
    Assegna una velocità massima ai punti dei quali non si è riuscito a recuperare la velocità massima.
    La velocità assegnata al singolo punto dipende dai punti adiacenti.

    :type speeds: int[]
    :param speeds: il vettore che contiene le velocità dell'intero viaggio
    '''
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

if __name__ == '__main__':
    nargs = len(sys.argv)
    if nargs == 1:
        print u"Per visualizzare i dettagli di un file txt di viaggio, digitare \"processing.py path/viaggio.txt\""
        print u"Per analizzare un viaggio, digitare \"processing.py path/viaggio.txt indice_viaggio\""
        print u"Per lanciare una demo, digita \"yes\""
        sys.stdout.flush()
        userchoice = raw_input()
        if userchoice == "yes" or userchoice == "Yes":
            viaggi = readViaggiTxt("input/2131428.txt",False)
            viaggio = viaggi[2]
            viaggio.punti = viaggio.punti[:10]
            try:
                analyze(viaggio)
            except urllib2.HTTPError as e:
                err = e.read()
                print err
        else:
            print "Bye!"
    elif nargs == 2:
        readViaggiTxt(sys.argv[1],True)
        print u"Per analizzare un viaggio, digitare \"processing.py path/viaggio.txt indice_viaggio\""
    elif nargs == 3:
        viaggi = readViaggiTxt(sys.argv[1],False)
        analyze(viaggi[int(sys.argv[2])])
    else:
        print u"Troppi paramentri"
        print u"Usage: Per visualizzare i dettagli di un file txt di viaggio, digitare \"processing.py path/viaggio.txt\""
        print u"Per analizzare un viaggio, digitare \"processing.py path/viaggio.txt indice_viaggio\""