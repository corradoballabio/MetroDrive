import urllib2

user = "Costeld"
path = "traces/"
filename = user + "_ids.txt"
f = open(filename, "r")

for l in f.readlines():
    
    id_ = l.rstrip()
    
    url = "https://www.openstreetmap.org/trace/" + id_ + "/data"
    ofile = path + id_ + ".gpx"
    
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