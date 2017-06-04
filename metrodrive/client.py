import sys, glob
import datetime, time
import json
import requests
import collector
import httplib2
from cryptography.fernet import Fernet

urlbase = "http://127.0.0.1:5000/metrodrive/api/v0.1/"
time_window = 2 #minute

class Client:
    def __init__(self, i , fic, fiv):
        ( self.device_id, self.shared_pwd ) = self.set_device_credentials(i, fic)
        self.file_input = fiv #txt con viaggi in input
        self.lista_viaggi = collector.json_txt_to_viaggi(fiv)
        
    def set_device_credentials(self, i, fn):
        f = open(fn, "r")
        l = f.readlines()[i+1].split("\t")
        return (l[0], l[1].rstrip())
        
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
                ppjson = {  "timestamp": p.timestamp,
                            "latitudine": p.latitudine,
                            "longitudine": p.longitudine,
                            "velocita": p.velocita 
                         }
                pjson_punti.append(ppjson)
               
            pjson = {   "tempo_inizio": v.tempo_inizio,
                        "punti": pjson_punti    } 
                        
            packets_json.append(pjson)
            
        return packets_json
            
          
    def send_data_viaggio(self, v):
        
        print v.id_, len(v.punti)
        vpackets = self.packets_from_viaggio(v) #estrai pacchetti viaggio come stringhe
        np = len(vpackets)
        
        http = httplib2.Http()
        headers = {'Content-Type': "application/json"}
        
        #effettua login
        chiper_suite = Fernet(self.shared_pwd)
        auth_data = { "device_id" : self.device_id, "signature" : chiper_suite.encrypt(self.device_id)}
        response, content = http.request(urlbase + "login", 'POST', json.dumps(auth_data), headers=headers)
        
        #invia dati
        headers['Cookie'] = response["set-cookie"]
        headers['Content-Type'] = "application/text"
        while len(vpackets) > 0:
            
            jdata = json.dumps(vpackets.pop(0)) #creo json data
            data = chiper_suite.encrypt(jdata) #cifro json data

            response, content = http.request(urlbase + "data", 'POST', data, headers=headers) 
            if response['status'] != '200': print "Error " + str(response) + str(content)
            if "set-cookie" in response: headers['Cookie'] = response["set-cookie"]
            
            time.sleep(1)
            
        #effettua logout
        response, content = http.request(urlbase + "logout", 'GET', headers=headers)
           
        print v.id_, ": " + str(np) + " pacchetti inviati."   
        
    def send_data_next_viaggio(self):
        
        if len(self.lista_viaggi) > 0:
            
            v = self.lista_viaggi.pop(0) #estrai viaggio da inviare
            
            self.send_data_viaggio(v) 

                
def main1():
    txt_files = glob.glob("input/*.txt")
    pwd_file = "keys"
    
    for txt_filename in txt_files:
        
        txt_filename = txt_files[2] #debug
        
        myclient = Client(1, pwd_file, txt_filename)
        print len(myclient.lista_viaggi)
        
        for v in myclient.lista_viaggi:
            myclient.send_data_viaggio(v)
            time.sleep(0)
            
        break
        
main1()