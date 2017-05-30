from datetime import datetime

class Punto:
    def __init__(self, timestamp, lat, lon, speed):
        self.timestamp = timestamp
        self.latitudine = lat
        self.longitudine = lon
        self.velocita = speed
        self.maxspeed = "-1"
        self.distance = "-1"

    def toString(self):
        return "Time: "+str(self.timestamp)+", Lat: "+str(self.latitudine)+", Lon: "+str(self.longitudine)+", Effective Speed: "+str(self.velocita)+", Max Speed: "+str(self.maxspeed)+", Distance: "+str(self.distance)
        
    def get_date(self):
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        ret = datetime.strptime(self.timestamp,fmt)
        return ret