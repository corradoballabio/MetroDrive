import sys, glob
import datetime
import json
import requests
import collector

# poi diventera' una classe

txt_files = glob.glob("output/*.txt")

time_window = 2 #minute

class Client:
    def __init__(self,fi):
        self.file_input = fi #txt con viaggi in input
        
    def packets_from_viaggio(self, v):
        
        packets = []
        
        vtstart = v.get_start_data()
        vpunti = v.get_punti()

        ptend = vtstart + datetime.timedelta(0,0,0,0,2) #aggiungi 2 minuti
        new_packet = [] 
        
        for p in vpunti:
            
            pdate = p.get_date()
            
            if pdate < ptend: 
                new_packet.append(p)
            else:
                if len(new_packet) > 0:
                    packets.append(new_packet)
                ptend = ptend + datetime.timedelta(0,0,0,0,2)
                new_packet = []
                new_packet.append(p)
        if len(new_packet) > 0:
            packets.append(new_packet)
                
        for p in packets:
            print len(p)
        
        
    def send_data(self):
        
        lv = collector.json_txt_to_viaggi(self.file_input)
        
        for v in lv:
            
            print v.id_, len(v.punti)
            packets = self.packets_from_viaggio(v)
                
            print "**"

                
def main1():
    txt_files = glob.glob("input/*.txt")
    
    for txt_filename in txt_files:
        
        myclient = Client(txt_filename)
        myclient.send_data()
        
        break
        
main1()