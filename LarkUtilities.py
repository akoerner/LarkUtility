#!/usr/bin/env python

###############################################################################
#                                                                             #
# copyright 2013 UNL Holland Computing Center                                 #
#                                                                             #
#  Licensed under the Apache License, Version 2.0 (the "License");            #
#     you may not use this file except in compliance with the License.        #
#    You may obtain a copy of the License at                                  #
#                                                                             #
#        http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                             #
#    Unless required by applicable law or agreed to in writing, software      #
#  distributed under the License is distributed on an "AS IS" BASIS,          #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#   See the License for the specific language governing permissions and       #
#   limitations under the License.                                            #
#                                                                             #
###############################################################################

###############################################################################
#                                                                             #
#                         L A R K   U t i l i t i e s                         #
#                                                                             #
###############################################################################

import re
import sys 
import os
import socket
import math
import sqlite3 as lite
import urllib
import urllib2
import BeautifulSoup

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
usage = "usage: LarkUtilities.py -l <ipaddress> -d <ipaddress1> <ipaddress2>"
os.chdir(dname)
sys.path.append('../../accessors')

"""
This python module contains a mechanisms and assorted methods for lark tasks
To generate HTML documentation for this module issue the
command:

    pydoc -w LarkUtilities

"""

__author__ =  'Andrew B. Koerner'
__email__ =  'AndrewKoerner.b@gmail.com'

__author__ =  'Bjorn Barrefors'

__organization__ = 'Holland Computing Center University of Nebraska - Lincoln'

class LarkUtilities(object):

###############################################################################
#                                                                             #
#                       H e l p e r   F u n c t i o n s                       #
#                                                                             #
###############################################################################

    @staticmethod
    def normalizeWhitespace(str):
        # Strip leading and trailing whitespace.
        # Make all remaining whitespace (tabs, etc) to spaces.
        # re is imported regular expression object
        # Pre: Any str
        # Post: Stripped leading and trailing whitespaces and all whitespace
        #       like tabs etc are now normal spaces.
        return re.sub(r'\s+', ' ', str.strip())
    
    @staticmethod
    def getGeody(IP):
        # Fetch location data from geody
        # Unknown behaviour on IPv6 address, only tested on IPv4
        # Check compatibility on geody.com
        # Pre: An IP address in str format
        # Post: BeautifulSoup data from geody, not str
        geody = "http://www.geody.com/geoip.php?ip=" + IP
        html_page = urllib2.urlopen(geody).read()
        soup = BeautifulSoup.BeautifulSoup(html_page)
        return soup('p')[3]

    @staticmethod
    def cityCountryParser(data):
        # Seperate city and country into two str's
        # Strip all else and return
        # Pre: BeautifulSoup data from geody
        # Post: A str with city, country and optionally state/province.
        #       CITY, [STATE/PROVINCE], COUNTRY
        geo_txt = re.sub(r'<.*?>', '', str(data))
        geo_txt = geo_txt[32:].upper().strip()
        stripped_data = geo_txt.strip("IP: ").partition(': ')
        city_country = stripped_data[2]
        stripped = city_country.partition(' (')
        city_txt = stripped[0]
        return city_txt

    @staticmethod
    def latLong(city_country):
        # Find latitude and longitude of city/country.
        # This function is not extremely accurate yet.
        # Would like to pick best result instead of first.
        # Pre: A str containing city, country and if available state/province. 
        #      CITY, [STATE/PROVINCE], COUNTRY
        # Post: Latitude and longitude of IP address in str format
        geody = "http://www.geody.com/geolook.php?world=terra&map=col&q=" + urllib.quote(city_country) + "&subm1=submit"
        html_page = urllib2.urlopen(geody).read()
        soup = BeautifulSoup.BeautifulSoup(html_page)
        link = soup('a')[10]
        strip1 = str(link).partition('Coords: ')
        strip2 = strip1[2].partition('\"')
        strip3 = strip2[0].partition(',')
        latitude = strip3[0]
        longitude = strip3[2]
        return latitude, longitude

    @staticmethod
    def IPGeolocate(IP):
        # Get data about IP address and parse it to extract city and country.
        # Translate city and country into longitude and latitude coordinates.
        # Pre: IP address in str format
        # Post: Longitude and latitude coordinates for IP address, str format
        raw_data = LarkUtilities.getGeody(IP)
        city_country = LarkUtilities.cityCountryParser(raw_data)
        print(city_country)
        # Return coordinates for antarctica if unknown position of IP
        if "UNKNOWN" in LarkUtilities.normalizeWhitespace(city_country):
            return str(-80), str(-100)
        latitude, longitude = LarkUtilities.latLong(city_country)
        return latitude, longitude

    @staticmethod
    def coordinateDiff(lat1, long1, lat2, long2):
        # Find distance between two coordinates
        # Haversine formula
        # Pre: latitude and longitude for two points in str
        # Post: Distance in km between the two points, float format
        R = 6371
        lat1 = float(lat1)
        lat2 = float(lat2)
        long1 = float(long1)
        long2 = float(long2)
        d_lat = math.radians((lat2-lat1))
        d_long = math.radians((long2-long1))
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)
        a = math.sin(d_lat/2)**2 + math.sin(d_long/2)**2 * math.cos(lat1) * math.cos(lat2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        return distance
    
    @staticmethod
    def IPDistance(IP1, IP2, con):
        # Given two IP addresses, find distance between these in real life
        # Pre: Two IP addresses in str format
        # Post: Distance in km between the two IP addresses in float
        lat1 = ""
        lat2 = ""
        long1 = ""
        long2 = ""
        with con:
            cur = con.cursor()
            cur.execute("SELECT EXISTS(SELECT * FROM IPtoCoord WHERE IP=? LIMIT 1)", [IP1])
            test = cur.fetchone()[0] 
            if int(test) == int(1):
                print "Fetch from cache 1"
                cur.execute('SELECT Lat FROM IPtoCoord Where IP=?', [IP1])
                lat1 = str(cur.fetchone()[0])
                cur.execute('SELECT Long FROM IPtoCoord Where IP=?', [IP1])
                long1 = str(cur.fetchone()[0])
            else:
                print "Fetch from Geody 1"
                lat1, long1 = LarkUtilities.IPGeolocate(IP1)
                cur.execute('INSERT INTO IPtoCoord VALUES(?,?,?)', (IP1,lat1,long1))
            cur.execute('SELECT EXISTS(SELECT * FROM IPtoCoord WHERE IP=? LIMIT 1)', [IP2])
            test = cur.fetchone()[0]
            if int(test) == int(1):
                print "Fetch from cache 1"
                cur.execute('SELECT Lat FROM IPtoCoord Where IP=?', [IP2])
                lat2 = (cur.fetchone()[0])
                cur.execute('SELECT Long FROM IPtoCoord Where IP=?', [IP2])
                long2 = (cur.fetchone()[0])
            else:
                print "Fetch from Geody 2"
                lat2, long2 = LarkUtilities.IPGeolocate(IP2)
                cur.execute('INSERT INTO IPtoCoord VALUES(?,?,?)', (IP2,lat2,long2))
        distance = LarkUtilities.coordinateDiff(lat1, long1, lat2, long2)        
        return distance

    #
    # Below are functions related to Lark
    #
   
    @staticmethod
    def ISO_3166_1_ALPHA_2_IpAddressGeoLocate(ipAddress):

        try:
            geody = "http://www.geody.com/geoip.php?ip=" + ipAddress
            htmlDocument = urllib2.urlopen(geody).read()
            soup = BeautifulSoup.BeautifulSoup(htmlDocument)
            paragraph = soup('p')[3]
            geo_txt = re.sub(r'<.*?>', '', str(paragraph))
        except:
            print htmlDocument
            return
        haystack = []
        dname = os.path.dirname(abspath)
        os.chdir(dname)
        
        lines = open("ISO_3166-1-alpha-2.txt", 'r').readlines()
        for line in lines:
            haystack.append(line.strip().split('\t',1))

        needle = geo_txt[32:].upper().strip()

        haystack = list(haystack)
        for index, key in enumerate(haystack):
            if  LarkUtilities.normalizeWhitespace(haystack[index][1]) in LarkUtilities.normalizeWhitespace(needle):
                tuple = (haystack[index][0], haystack[index][1], needle);
                return tuple

    #@staticmethod
    #def whois(ipAddressOrHostName, attributes):

###############################################################################
#                                                                             #
#                                 M a i n                                     #
#                                                                             #
###############################################################################

def main(argv):
    if len(argv) == 2:
        # Two IP addresses, find the distance between them
        # Initialize SQLite3 db to check if IP is in cache
        con = lite.connect('ip_cache.db')
        with con:
            cur = con.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS IPtoCoord (IP TEXT, Lat TEXT, Long TEXT)')
        # To implement: Check valid IP in argv[0] and argv[1]
        distance = LarkUtilities.IPDistance(str(argv[0]), str(argv[1]), con)
        print distance
        sys.exit()
    elif len(argv) == 1:
        # One IP address, find geolocation
        # Initialize SQLite3 db to check if IP is in cache
        # To implement: Check valid IP in argv[0]
        LarkUtilities.ISO_3166_1_ALPHA_2_IpAddressGeoLocate(argv[0])
        sys.exit()
    else:
        print usage
        sys.exit()

if __name__=="__main__":
    main(sys.argv[1:])
