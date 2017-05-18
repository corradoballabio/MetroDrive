# -*- coding: utf-8 -*-
import overpass

def main():
    coords01 = ["45.41090,9.27177","45.41876,9.27240","45.41907,9.26239","45.42449,9.26539","45.42636,9.25609","45.4186, 9.25411"]
    #coords01 =["45.4186, 9.25411","45.41876,9.27240"]
    maxspeeds = []
    for coord in coords01:
        maxspeeds.append(getMaxspeed(coord))
        
def getMaxspeed(coord):
    api = overpass.API()
    query = '(around:1,%s)' % (coord)
    way_query = overpass.WayQuery(query)
    response = api.Get(way_query)
    results = response["features"]
    roads = []
    
    #primo filtraggio: per ogni coordinata assegno una o più strade, eliminando tutto il resto
    for result in results:
        if result["properties"]:
            result = result["properties"]
            if "highway" in result:
                if "motorway" in result["highway"]: roads.append(result)
                if "trunk" in result["highway"]:
                    print "TRUNK!!!!"
                    roads.append(result)
                if "primary" in result["highway"]: roads.append(result)
                if "secondary" in result["highway"]: roads.append(result)
                if "tertiary" in result["highway"]: roads.append(result)
                if "unclassified" in result["highway"]: roads.append(result)
                if "residential" in result["highway"]: roads.append(result)
    
    #se più di una strada passa il filtraggio, bisogna tenere la più significativa            
    if len(roads)>1:
        mask = []
        for road in roads:
            if "maxspeed" in road: mask.append(road)
        if len(mask)>1 : print "PIU' DI UNA STRADA SOPRAAVVISSUTA AL FILTRAGGIO"
        roads = mask        
    
    #a questo punto dovrebbe esserci solo un elento all'interno dell'array
    road = roads[0]
    maxspeed = 0
    
    #se c'è il tag "maxspeed" allora prendo direttamente quel valore
    if "maxspeed" in road:
        maxspeed = int(road["maxspeed"])

    #se il tipo di "highway" è "residential" o "motorway" allora non serve differenziare tra strada urbana o interurbana
    if maxspeed==0:
        if "residential" in road["highway"]:
            maxspeed = 50
        if "motorway" in road["highway"]:
            maxspeed = 130
    
    #se gli if precedenti falliscono allora controllo se la strada è urbana o interurbana (tramite presenza o meno del marciapiede) e poi controllo il tipo di strada (primary, secondary,tertiary o unclassified)
    if maxspeed==0:
        speeds = {
                "urban" : {"primary" : 50, "secondary" : 50, "tertiary" : 50, "unclassified" : 50}, 
                "interurban" : {"primary" : 90, "secondary" : 90, "tertiary" : 90, "unclassified" : 70}
                  }
        type = None
        if "sidewalk" in road: type="urban"
        else: type="interurban"
        maxspeed = speeds[type][road["highway"]]
        
    print road,"Velocità massima:",maxspeed,"km/h"
    return maxspeed

if __name__ == '__main__':
    main()

    
    
    