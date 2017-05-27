import urllib2
import time

#These variables should be adjusted to meet your requirements, 
#see http://wiki.openstreetmap.org/wiki/API_v0.6#Retrieving_GPS_points for more information

#Boundary Box

top_left = "45.804744479698236,9.076429898070451"
bottom_right = "45.48793003663358,9.699904019164391"

minlon = top_left.split(",")[1]
minlat = bottom_right.split(",")[0]
maxlon = bottom_right.split(",")[1]
maxlat = top_left.split(",")[0]

#Start downloading
page = 0

#Using OSM API V0.6
url = "http://api.openstreetmap.org/api/0.6/trackpoints?bbox="+minlon+","+minlat+","+maxlon+","+maxlat+"&page="+str(page)

url = "https://www.openstreetmap.org/trace/2414568/data"

print url

file_prefix = "download_"
file_suffix = ".gpx"

while True:
    try:
        file_name = file_prefix+str(page)+file_suffix
        u = urllib2.urlopen(url)#+str(page))
        f = open(file_name, 'wb')
        #meta = u.info()
        #file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading: %s" % (file_name)

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            #status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            #status = status + chr(8)*(len(status)+1)
            #print status,

        f.close()
        
        page += 1
        time.sleep(60)
    except urllib2.HTTPError ,e:
        print "Download stopped; HTTP Error - %s" % e.code
        break
