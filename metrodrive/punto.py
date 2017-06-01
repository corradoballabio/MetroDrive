from datetime import datetime

class Punto:
    def __init__(self, timestamp, lat, lon, speed):
        self.timestamp = timestamp
        self.latitudine = lat
        self.longitudine = lon
        self.velocita = speed
        self.maxspeed = -3
        self.distance = -3

    def __str__(self):
        return "Time:\t\t"+str(self.timestamp)+"\nLat:\t\t"+str(self.latitudine)+"\nLon:\t\t"+str(self.longitudine)+"\nSpeed:\t\t"+str(self.velocita)+"\nMax Speed:\t"+str(self.maxspeed)+"\nDistance:\t"+str(self.distance)
        
    def get_date(self):
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        ret = datetime.strptime(self.timestamp,fmt)
        return ret

    def setMaxSpeed(self,maxspeed):
        self.maxspeed = int(maxspeed)

    def setDistance(self,distance):
        self.distance = int(distance)