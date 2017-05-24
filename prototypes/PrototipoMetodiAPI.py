# -*- coding: utf-8 -*-
import overpass
import requests
import osrm
osrm.RequestConfig.host = "router.project-osrm.org"

def main():
    coords01 = ["45.41090,9.27177","45.41876,9.27240","45.41907,9.26239","45.42449,9.26539","45.42636,9.25609","45.4186, 9.25411"]
    percorso = ["45.415797350334074,9.26553636245703","45.41588019323612,9.265718752669725","45.41596303601664,9.265944058226951","45.416151314611966,9.266426855849582","45.41624921923352,9.266630703734993","45.41636218589344,9.266952568816748","45.41647515232733,9.26722078971761","45.4166182428194,9.26749973945573","45.41673120874105,9.267767960356592","45.41683664339716,9.268025452421995","45.416919484774525,9.26826148681558","45.4170475121194,9.26848679237281","45.41718307016777,9.268744284438212","45.41729603495948,9.269001776503615","45.41740899952519,9.269280726241735","45.4175069019656,9.269570404815314","45.417860855528154,9.270943695830496","45.41796628807502,9.271147543715907","45.418094313045884,9.271383578109493","45.4182901153818,9.271641070174896","45.418448262926326,9.271812731551233","45.418576286804424,9.272005850600285","45.418726902760625,9.27238135986293","45.41884739523554,9.272649580763794","45.418945295182674,9.272885615157378","45.41905072570465,9.273121649550964","45.419178748217405,9.273454243468178","45.41930677043922,9.273690277861764","45.41946491513628,9.273979956435342","45.4196230593904,9.274301821517096","45.41976614190553,9.274537855910681","45.419871570894806,9.274741703796092","45.42002971400996,9.274688059615201","45.42012008130545,9.274559313582499","45.4202330402214,9.274430567549798","45.42037612119077,9.274258906173461","45.42052673234533,9.274087244796226","45.42069240415172,9.273861939239","45.42082795344975,9.273733193206297","45.42149063422249,9.272885615157378","45.42164877280278,9.272724682616502","45.42179938056244,9.272510105895632","45.421965048634505,9.272306258010222","45.422138246553274,9.272091681289352","45.42223614079439,9.272005850600285","45.42256747388852,9.27160888366672","45.422725609452606,9.27140503578131","45.422921395728174,9.271126086043191","45.4230117583954,9.271008068846847","45.423117181324166,9.270804220961438","45.42320754367802,9.270557457732393","45.4233581472795,9.27023559265064","45.42344850924766,9.269999558257052","45.423568991647116,9.269709879683473","45.42367441353531,9.269398743438076","45.42376477499726,9.269151980209033","45.423885256721746,9.268862301635455","45.424005738189145,9.26860480957005","45.4240810389751,9.268411690520997","45.42417139978621,9.26819711379923","45.42424670035185,9.267971808242002","45.42434459093698,9.267725045012957","45.42443495132625,9.26749973945573","45.42454790160941,9.267328078078494","45.424615671670836,9.267102772521268","45.424721091604496,9.266920382308573","45.42478133147873,9.266748720931338","45.42490934099693,9.26643758468594","45.42498464057828,9.266158634947821","45.425203008795364,9.26561146430884","45.4252557182387,9.265450531767964","45.42533854726398,9.265225226210735","45.425436435955824,9.26497846298169","45.42554938423523,9.264731699751747","45.42566233228865,9.264678055571755","45.42579033980913,9.264951640891693","45.427744300929845,9.268207842635587","45.42784971502095,9.26841705493828","45.427906186774884,9.268497521209166","45.4280793664669,9.268776470946387","45.428158426584815,9.268669182586402","45.42905066880717,9.267601663398436","45.42908078644158,9.267548019217545","45.42914855106121,9.267505103873907","45.429246433146126,9.267376357841208","45.42928031536635,9.26729052715214","45.4293066681906,9.267236882972147","45.4293405503753,9.267151052283978","45.429366903171434,9.267070586013093","45.42939325595462,9.266963297652207","45.429434667447566,9.266759449767696","45.429476078909474,9.26643758468594","45.42948360826252,9.266351753996874","45.429525019689166,9.266335660743236","45.42957772509622,9.266367847251411","45.42958148976641,9.266577059554102","45.42955890174217,9.266759449767696"]
    
    maxspeeds = getMaxSpeedTest(coords01)
    print maxspeeds
    
    distances = getDistanceTest(coords01)
    print distances
    
def getMaxSpeedTest(coords):
    maxspeeds = []
    for coord in coords:
        maxspeeds.append(getMaxspeed(coord))
    return maxspeeds

def getDistanceTest(coords):
    distances = []
    i = 0
    while i<len(coords)-2:
        distances.append(getDistance(coords[i],coords[i+1]))
        i = i + 1
    return distances
    
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

def getDistance(inputCoord1,inputCoord2):
    coord1 = swapCoords(inputCoord1)
    coord2 = swapCoords(inputCoord2)
    result = osrm.simple_route(coord1, coord2)
    #print result
    distance = result["routes"][0]["legs"][0]["distance"]
    print distance, "metri"
    return distance
    
def swapCoords(strCoord):
    coord = strCoord.split(",")
    return (float(coord[1]),float(coord[0]))
    
if __name__ == '__main__':
    main()  