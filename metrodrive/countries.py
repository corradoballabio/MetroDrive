#!/usr/bin/env python
# -*- coding: utf-8 -*-

from osgeo import ogr
import os


class Point(object):

    def __init__(self, lat, lng):
        self.point = ogr.Geometry(ogr.wkbPoint)
        self.point.AddPoint(lng, lat)
    
    def getOgr(self):
        return self.point
    ogr = property(getOgr)

class Country(object):
   
    def __init__(self, shape):
        self.shape = shape
    
    def getIso(self):
        return self.shape.GetField('ISO2')
    iso = property(getIso)
    
    def __str__(self):
        return self.shape.GetField('NAME')
    
    def contains(self, point):
        return self.shape.geometry().Contains(point.ogr)

class CountryChecker(object):
    
    def __init__(self, country_file):
        driver = ogr.GetDriverByName('ESRI Shapefile')
        self.countryFile = driver.Open(country_file)
        self.layer = self.countryFile.GetLayer()
    
    def getCountry(self, point):
        for i in xrange(self.layer.GetFeatureCount()):
            country = self.layer.GetFeature(i)
            if country.geometry().Contains(point.ogr):
                return Country(country)

        return None

        
#point = Point(41.894549, 12.478287)
#cc = CountryChecker("TM_WORLD_BORDERS-0.3.shp")
#print cc.getCountry(point).iso