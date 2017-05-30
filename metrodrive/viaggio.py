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