from datetime import datetime

class Punto:
    def __init__(self, timestamp, lat, lon, speed):
        self.timestamp = timestamp
        self.latitudine = lat
        self.longitudine = lon
        self.velocita = speed
        self.maxspeed = -3
        self.distance = -3

    # def __init__(self):
    #     self.timestamp = "0"
    #     self.latitudine = ""
    #     self.longitudine = ""
    #     self.velocita = ""
    #     self.maxspeed = -3
    #     self.distance = -3

    def fromJSON(self,json):
        self.timestamp = json["timestamp"]
        self.latitudine = json["latitudine"]
        self.longitudine = json["longitudine"]
        self.velocita = json["velocita"]

    def toJSON(self):
        timestamp = "\"timestamp\" : \""+str(self.timestamp)+"\""
        lat = "\"latitudine\" : \""+str(self.latitudine)+"\""
        lon = "\"longitudine\" : \""+str(self.longitudine)+"\""
        vel = "\"velocita\" : \""+str(self.velocita)+"\""
        maxvel = "\"maxvel\" : \""+str(self.maxspeed)+"\""
        dist = "\"distance\" : \""+str(self.distance)+"\""
        return str("{ "+timestamp+", "+lat+", "+lon+", "+vel+", "+maxvel+", "+dist+" }")

    def __str__(self):
        return "Time:\t\t"+str(self.timestamp)+"\nLat:\t\t"+str(self.latitudine)+"\nLon:\t\t"+str(self.longitudine)+"\nSpeed:\t\t"+str(self.velocita)+" km/h"+"\nMax Speed:\t"+str(self.maxspeed)+" km/h"+"\nDistance:\t"+str(self.distance)+" m"
        
    def get_date(self):
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        ret = datetime.strptime(self.timestamp,fmt)
        return ret

    def setMaxSpeed(self,maxspeed):
        self.maxspeed = int(maxspeed)

    def setDistance(self,distance):
        self.distance = int(distance)