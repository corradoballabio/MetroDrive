import sys, glob
import datetime, time
import json
import requests
import collector
import httplib2


urlbase = "http://127.0.0.1:5000/metrodrive/api/v0.1/"
txt_files = glob.glob("output/*.txt")
time_window = 2 #minute

class Client:
    def __init__(self, d_id, fi):
        self.device_id = d_id
        self.file_input = fi #txt con viaggi in input
        self.lista_viaggi = collector.json_txt_to_viaggi(fi)
        
    def packets_from_viaggio(self, v):
        
        packets_point = []
        
        v_id = v.id_
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
                    packets_point.append(new_packet)
                ptend = ptend + datetime.timedelta(0,0,0,0,2)
                new_packet = []
                new_packet.append(p)
        if len(new_packet) > 0:
            packets_point.append(new_packet)
           
        packets_json = []
             
        for pp in packets_point:
            
            pjson_punti = []
            
            for p in pp:
                ppjson = {  'timestamp': p.timestamp,
                            'latitudine': p.latitudine,
                            'longitudine': p.longitudine,
                            'velocita': p.velocita 
                         }
                pjson_punti.append(ppjson)
               
            pjson = {   'device_id': self.device_id,
                        'viaggio_id': v_id,
                        'punti': pjson_punti    } 
                        
            packets_json.append(pjson)
            
        return packets_json
            
          
    def send_data_viaggio(self, v):
        
        print v.id_, len(v.punti)
        vpackets = self.packets_from_viaggio(v) #estrai pacchetti viaggio
        np = len(vpackets)
        
        http = httplib2.Http()
        content_type_header = "application/json"
        
        http.request(urlbase + "login", 'POST', body=self.device_id, headers={'content-type':'text/plain'})
        
        while len(vpackets) > 0:
        
            data = vpackets.pop(0)
            
            #invio dati
            
            headers = {'Content-Type': content_type_header}
            response, content = http.request(urlbase + "data", 'POST', json.dumps(data), headers= headers) 
            if response != 200: print "Error " + str(response)
            
            time.sleep(1)
            
            #return #debug
           
        print v.id_, ": " + str(np) + " pacchetti inviati."   
        
    def send_data_next_viaggio(self):
        
        if len(self.lista_viaggi) > 0:
            
            v = self.lista_viaggi.pop(3) #estrai viaggio da inviare
            
            self.send_data_viaggio(v) 

                
def main1():
    txt_files = glob.glob("input/*.txt")
    
    for txt_filename in txt_files:
        
        myclient = Client("00000", txt_filename)
        
        for v in myclient.lista_viaggi:
            myclient.send_data_next_viaggio()
            time.sleep(0)
            break

        
main1()