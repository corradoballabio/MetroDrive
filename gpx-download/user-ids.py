import urllib2
from bs4 import BeautifulSoup as bsoup

user = "Costeld"

url_base = "https://www.openstreetmap.org/user/" + user + "/traces/page/"
fl = open(user + "_ids.txt", "w+")

tcount = 0
npage = 1

while True:
    
    print npage   
    
    url = url_base + str(npage)
    h = urllib2.urlopen(url)       
    content = bsoup(h)
    
    ids = set()
    
    for link in content.find_all('td', class_="table0"):
        id_ = link.a['href'].split("/")[-1]
        ids.add(id_)

    if len(ids) == 0:
        print "END: %s %s" % (tcount, npage)
        break
    
    for id_ in ids:
        tcount += 1
        fl.write(id_+"\n")
    
    npage += 1
  