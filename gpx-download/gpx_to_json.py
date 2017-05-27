from bs4 import BeautifulSoup as soup
import json
import os, glob

class Punto:
    def __init__(self, timestamp, lat, lon, speed):
        self.timestamp = timestamp
        self.latitudine = lat
        self.longitudine = lon
        self.velocita = speed

class Viaggio:
    def __init__(self, id_, tstart=-1, tend=-1, punti_list=[]):
        self.id_ = id_
        self.tempo_inizio = tstart
        self.tempo_fine = tend
        self.punti = punti_list
    
    def addPoint(self, punto):
        self.punti.append(punto)


def gpx_to_viaggi(filename):
    
    ftrace = open(filename, "r")
    gpx_trace = ftrace.read()
    soup_trace = soup(gpx_trace)
    
    nseg = 0
    file_id = filename.split(".")[0].split("/")[-1]
    print file_id
    viaggi_list = []
    
    for segment in soup_trace.findAll('trkseg'):
        
        id_viaggio = file_id + str(nseg)
        new_viaggio = Viaggio(id_viaggio, -1, -1, [])
        
        for point in segment.findAll('trkpt'):
            
            lat = point["lat"]
            lon = point["lon"]
            time = point.time.string
            gpxspeed = point.find('gpxtpx:speed')
            
            if gpxspeed != None: #aggiunta punto solo se con speed
            
                speed = gpxspeed.string
                #print lat, lon, time, speed
                new_point = Punto(time,lat,lon,speed)
                new_viaggio.addPoint(new_point)
        
        if len(new_viaggio.punti) > 0:        
            viaggi_list.append(new_viaggio)
            nseg += 1

    #print "END: " + str(nseg)
    ftrace.close()
    
    return viaggi_list
    
def viaggi_to_json_txt(lista_viaggi, filename_output ):
    
    ftxtout = open(filename_output, "w")
    
    lout = []
    
    for v in lista_viaggi:
        lv = [v.id_, v.tempo_inizio, v.tempo_fine]
        for p in v.punti:
            lv.append([p.timestamp, p.latitudine, p.longitudine, p.velocita])
        lout.append(lv)
        
    json.dump(lout, ftxtout)
    
    ftxtout.close()
    
    print filename_output
    
def json_txt_to_viaggi(filename_input):
    
    ftxtin = open(filename_input, "r")
    
    lout = []
    
    lv = json.loads(ftxtin.read())

    for v in lv:
        id_ = v[0]
        inizio = v[1]
        fine = v[3]
        new_viaggio = Viaggio(id_, inizio, fine, [])
        for p in v[4:]:
            time = p[0]
            lat = p[1]
            lon = p[2]
            speed = p[3]
            new_point = Punto(time, lat, lon, speed)
            new_viaggio.addPoint(new_point)
        lout.append(new_viaggio)
        
    return lout
    #print len(lout[2].punti)
    
    
#main

def main1():
    gpx_files = glob.glob('traces/*.gpx')
    path_out = "txt_out/"

    for gpx_filename in gpx_files:
    
        lv = gpx_to_viaggi(gpx_filename)
    
        filename_out = path_out + gpx_filename.split(".")[0].split("/")[-1] + ".txt"
      
        viaggi_to_json_txt(lv, filename_out)


def main2():
    filename = "txt_out/1993723.txt"
    json_txt_to_viaggi(filename)
    
main2()
    
    
   