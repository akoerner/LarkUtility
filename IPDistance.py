###############################################################################
#                                                                             #
#                            I P   D i s t a n c e                            #
#                                                                             #
###############################################################################

"""
Class find distance in real world between two IP addresses. 

Script take two arguments, two IP addresses.
Find the city and country of each IP address using geody.com's service.
Look up the city in pre existing table for long and lat coordinates.
Calculate the distance between coordinates.

If city is not already in the table, use google's service to find long and lat.

"""

import re
import sys 
import math
import urllib2
import urllib
import BeautifulSoup

usage = "Run the script: ./IP_Distance.py IPAddress1 IP Address2"

def normalizeWhitespace(str):
    # Strip leading and trailing whitespace.
    # Make all remaining whitespace (tabs, etc) to spaces.
    # re is imported regular expression object
    return re.sub(r'\s+', ' ', str.strip())
    
def getGeody(IP):
    # Fetch location data from geody
    geody = "http://www.geody.com/geoip.php?ip=" + IP
    html_page = urllib2.urlopen(geody).read()
    soup = BeautifulSoup.BeautifulSoup(html_page)
    return soup('p')[3]

def getCountries():
    # Get a list of all countries from file.
    # Is used for comparison later. File written in ISO standard
    countries = []
    lines = open("countries.txt", 'r').readlines()
    for line in lines:
        countries.append(line.strip().split('\t',1))
    return countries

def cityCountryParser(data):
    # Seperate city and country into two str's
    # Strip all else and return
    geo_txt = re.sub(r'<.*?>', '', str(data))
    geo_txt = geo_txt[32:].upper().strip()
    stripped_data = geo_txt.strip("IP: ").partition(': ')
    city_country = stripped_data[2]
    stripped = city_country.partition(' (')
    city_txt = stripped[0]
    return city_txt

def latLong(city_country):
    # Find latitude and longitude of city/country.
    # This function is not extremely accurate yet.
    # Would like to pick best result instead of first.
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

def IPGeolocate(IP):
    # Get data about IP address and parse it to extract city and country.
    # Translate city and country into longitude and latitude coordinates.
    raw_data = getGeody(IP)
    city_country = cityCountryParser(raw_data)
    print(city_country)
    # Return coordinates for antarctica if unknown
    if "UNKNOWN" in normalizeWhitespace(city_country):
        return str(-80), str(-100)
    latitude, longitude = latLong(city_country)
    return latitude, longitude

def coordinateDiff(lat1, long1, lat2, long2):
    # Find distance between two coordinates
    # Haversine formula
    R = 6371
    lat1 = float(lat1)
    lat2 = float(lat2)
    long1 = float(long1)
    long2 = float(long2)
    d_lat = math.radians((lat2-lat1))
    d_long = math.radians((long2-long1))
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    a = math.sin(d_lat/2)**2 +  math.sin(d_long/2)**2 * math.cos(lat1) * math.cos(lat2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance

def IPDistanceFunc(IP1, IP2):
    # Given two IP addresses, find distance between these in real life
    lat1, long1 = IPGeolocate(IP1)
    lat2, long2 = IPGeolocate(IP2)
    print (lat1 + "," + long1 + " | " + lat2 + "," + long2)
    distance = coordinateDiff(lat1, long1, lat2, long2)
    return distance

# Script starts
if len(sys.argv)!=3:
    print(usage)
    sys.exit(0)
else:
    IP1 = sys.argv[1]
    IP2 = sys.argv[2]

distance = IPDistanceFunc(IP1, IP2)
print(distance)
