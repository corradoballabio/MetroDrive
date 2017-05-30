from datetime import datetime

class Punto:
    def __init__(self, timestamp, lat, lon, speed):
        self.timestamp = timestamp
        self.latitudine = lat
        self.longitudine = lon
        self.velocita = speed
        
    def get_date(self):
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        ret = datetime.strptime(self.timestamp,fmt)
        return ret