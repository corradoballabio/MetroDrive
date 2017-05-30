from datetime import datetime

class Viaggio:
    def __init__(self, id_, tstart, tend, punti_list):
        self.id_ = id_
        self.tempo_inizio = tstart
        self.tempo_fine = tend
        self.punti = punti_list
    
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

    def toOsrmFormat(coords):
        #Le api OSM utilizzano coordinate in formato Longitudine, Latitudine, sottoforma di tupla di float
        swappedCoords = []
        for coord in coords:
            coord = strCoord.split(",")
            swappedCoords.append((float(coord[1]),float(coord[0]))) 
        return swappedCoords

    def numPunti(self):
        return len(self.punti)