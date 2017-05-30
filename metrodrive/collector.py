from bs4 import BeautifulSoup as soup
import json
import os, glob, sys
import urllib2

from punto import Punto
from viaggio import Viaggio

maxlat = -90
maxlon = -180
minlat = 90
minlon = 180

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
        new_viaggio = Viaggio(id_viaggio, "", "", [])
        lasttime = "" #tempo ultimo punto aggiunto a viaggio
        
        for point in segment.findAll('trkpt'):
            
            lat = point["lat"]
            lon = point["lon"]
            time = point.time.string
            gpxspeed = point.find('gpxtpx:speed')
            
            if gpxspeed != None: #aggiunta punto solo se con speed
            
                speed = gpxspeed.string
                if lasttime == "": new_viaggio.tempo_inizio = time #primo punto
                lasttime = time
                #print lat, lon, time, speed
                new_point = Punto(time,lat,lon,speed)
                new_viaggio.addPoint(new_point)
        
        if len(new_viaggio.punti) > 0: 
            new_viaggio.tempo_fine = lasttime #ultimo punto       
            viaggi_list.append(new_viaggio)
            nseg += 1

    #print "END: " + str(nseg)
    ftrace.close()
    
    return viaggi_list
    
def viaggi_to_json_txt(lista_viaggi, filename_output ):
    
    global maxlat, maxlon, minlat, minlon
    
    ftxtout = open(filename_output, "w")
    
    lout = []
    
    for v in lista_viaggi:
        lv = [v.id_, v.tempo_inizio, v.tempo_fine]
        for p in v.punti:
            if float(p.latitudine) > maxlat: maxlat = float(p.latitudine)
            if float(p.latitudine) < minlat: minlat = float(p.latitudine)
            if float(p.longitudine) > maxlon: maxlon = float(p.longitudine)
            if float(p.longitudine) < minlon: minlon = float(p.longitudine)
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
        fine = v[2]
        new_viaggio = Viaggio(id_, inizio, fine, [])
        for p in v[3:]:
            time = p[0]
            lat = p[1]
            lon = p[2]
            speed = p[3]
            new_point = Punto(time, lat, lon, speed)
            new_viaggio.addPoint(new_point)
        lout.append(new_viaggio)
        
    return lout


def get_user_ids(username):
    
    opath = username + "_ids.txt"
    url_base = "https://www.openstreetmap.org/user/" + username + "/traces/page/"
    fl = open(opath, "w+")

    tcount = 0
    npage = 1

    while True:
  
        url = url_base + str(npage)
        h = urllib2.urlopen(url)       
        content = bsoup(h)
    
        ids = set()
    
        for link in content.find_all('td', class_="table0"):
            id_ = link.a['href'].split("/")[-1]
            ids.add(id_)

        if len(ids) == 0:
            #print "END: %s %s" % (tcount, npage)
            break
    
        for id_ in ids:
            tcount += 1
            fl.write(id_+"\n")
            
        npage += 1
    
    return opath

def get_user_gpx(username, opath):
    
    path_ids = get_user_ids(username)
    f = open(path_ids, "r")

    for l in f.readlines():
    
        id_ = l.rstrip()
    
        url = "https://www.openstreetmap.org/trace/" + id_ + "/data"
        ofile = opath + id_ + ".gpx"
    
        try:
            u = urllib2.urlopen(url)
            fo = open(ofile, 'wb')
            print "Downloading: %s" % (ofile)

            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break
                file_size_dl += len(buffer)
                fo.write(buffer)

            fo.close()

        except urllib2.HTTPError ,e:
            print "Download stopped; HTTP Error - %s" % e.code
            break
            
    f.close()
            
    return
    
#main

def main1():
    gpx_files = glob.glob('gpx/*.gpx')
    path_out = "input/"

    for gpx_filename in gpx_files:
    
        lv = gpx_to_viaggi(gpx_filename)
    
        filename_out = path_out + gpx_filename.split(".")[0].split("/")[-1] + ".txt"
      
        viaggi_to_json_txt(lv, filename_out)
        
    print maxlat, maxlon, minlat, minlon
    #55.967437 28.791064 38.577169 -9.339771

def main2():
    filename = "txt_out/1993723.txt"
    json_txt_to_viaggi(filename)
    
if __name__=="__main__":
    main1()
    
    
   