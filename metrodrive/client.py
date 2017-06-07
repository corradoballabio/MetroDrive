import sys, glob
import datetime, time
import json
import requests
import collector
import httplib2
from cryptography.fernet import Fernet

urlbase = "http://192.168.0.101:5000/metrodrive/api/v0.1/"
time_window = 2 #minute

class Client:
    def __init__(self, did, pwd, vv):
        """
        Rappresenta il client che invia al server i dati grezzi dei viaggi 
        prelevati dai dongle interni ai veicoli. 
        
        :type did: string
        :param did: identificativo del dispositivo 
        :type pwd: string
        :param pwd: password simmetrica condivisa tra dispositivo e server
        :type vv: Viaggio[]
        :param vv: lista di viaggi associati al dispositivo
        
        """
        self.device_id = did
        self.shared_pwd = pwd
        self.lista_viaggi = vv
        
    def packets_from_viaggio(self, v):
        """
        Estrae i punti di un oggetto Viaggio, li divide per finestre temporali di lunghezza time_window e
        crea delle liste di punti in formato json rappresentanti i pacchetti di invio del Client.
        
        :type v: Viaggio
        :param v: Viaggio in input
        :rtype: lista di dizionari json
        :return: lista dei pacchetti di invio contenente i punti del viaggio di input
        """
        
        packets_point = []
        
        v_id = v.id_
        vtstart = v.get_start_data()
        vpunti = v.get_punti()

        # partiziono i punti secondo finestre temporali di lunghezza time_window minuti
        ptend = vtstart + datetime.timedelta(0,0,0,0,time_window)
        new_packet = [] 
        
        for p in vpunti:
            
            pdate = p.get_date()
            
            if pdate < ptend: 
                new_packet.append(p)
            else:
                if len(new_packet) > 0:
                    packets_point.append(new_packet)
                ptend = ptend + datetime.timedelta(0,0,0,0,time_window)
                new_packet = []
                new_packet.append(p)
        if len(new_packet) > 0:
            packets_point.append(new_packet)
           
        packets_json = []
        
        # converto le liste di punti in formato json
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
        """
        Invia in sicurezza al Server i dati grezzi contenuti in un viaggio in input.
            
        :type v: Viaggio
        :param v: viaggio rappresentante l'insieme di punti da inviare al Server    
        """
        
        #estrai pacchetti dal viaggio come stringhe di dizionari
        #print v.id_, len(v.punti)
        vpackets = self.packets_from_viaggio(v) 
        np = len(vpackets)
        
        http = httplib2.Http()
        headers = {'Content-Type': "application/json"}
        
        #effettua login
        chiper_suite = Fernet(self.shared_pwd)
        auth_data = { "device_id" : self.device_id, "signature" : chiper_suite.encrypt(self.device_id)}
        response, content = http.request(urlbase + "login", 'POST', json.dumps(auth_data), headers=headers)
        if response['status'] != '200': print "Login error " + str(response) + str(content)
        else: print "Dispositivo %s connesso. Inizio invio viaggio %s.\n" % (self.device_id, v.id_)
        
        #invia dati
        headers['Cookie'] = response["set-cookie"]
        headers['Content-Type'] = "application/text"
        for pi in range(len(vpackets)):
            
            jdata = json.dumps(vpackets[pi]) #creo json data
            data = chiper_suite.encrypt(jdata) #cifro json data

            response, content = http.request(urlbase + "data", 'POST', data, headers=headers) 
            if response['status'] != '200': print "Error " + str(response) + str(content)
            else: print "Inviato pacchetto %s di %s" % (pi, len(vpackets))
            if "set-cookie" in response: headers['Cookie'] = response["set-cookie"]
            
            time.sleep(1)
            
        #effettua logout
        response, content = http.request(urlbase + "logout", 'GET', headers=headers)
        if response['status'] != '200': print "Logout error " + str(response) + str(content)
        else: print "Dispositivo %s disconnesso. Invio viaggio %s terminato.\n" % (self.device_id, v.id_) 

                
def main1():
    from random import randint
    i_user = randint(0,100)
    i_txt = randint(0,23)
    pwd_file = "keys"
    f_pwd = open(pwd_file, "r")
    l = f_pwd.readlines()[i_user+1].split("\t")
    
    txt_files = glob.glob("input/*.txt")
    txt_filename = txt_files[i_txt]
    viaggi = collector.json_txt_to_viaggi(txt_filename)
    
    myclient = Client(l[0], l[1], viaggi)
    
    for v in myclient.lista_viaggi:
        myclient.send_data_viaggio(v)
        time.sleep(1)
    
        
main1()