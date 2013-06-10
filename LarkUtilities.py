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
import urllib2
import BeautifulSoup
import PerfSonarAccessor

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
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
        return re.sub(r'\s+', ' ', str.strip())
    
    @staticmethod
    def getGeody(IP):
        # Fetch location data from geody
        geody = "http://www.geody.com/geoip.php?ip=" + IP
        html_page = urllib2.urlopen(geody).read()
        soup = BeautifulSoup.BeautifulSoup(html_page)
        return soup('p')[3]

    @staticmethod
    def getCountries():
        # Get a list of all countries from file.
        # Is used for comparison later. File written in ISO standard
        countries = []
        lines = open("countries.txt", 'r').readlines()
        for line in lines:
            countries.append(line.strip().split('\t',1))
        return countries

    @staticmethod
    def cityCountryParser(data):
        # Seperate city and country into two str's
        # Strip all else and return
        # Check for unknown city/country
        geo_txt = re.sub(r'<.*?>', '', str(data))
        geo_txt = geo_txt[32:].upper().strip()
        stripped_data = geo_txt.strip("IP: ").partition(': ')
        city_country = stripped_data[2]
        stripped = city_country.partition(' (')
        city_txt = stripped[0]
        #if normalizedWhtiespace("unknown")
        #for i, key in enumerate(countries):
        #    if  normalize_whitespace(countries[i][1]) in normalize_whitespace(city_country):
        #        print haystack[i][1]
        #        break
        return city_txt

    @staticmethod
    def latLong(city_country):
        # Find latitude and longitude of city/country.
        return latitude, longitude

    @staticmethod
    def coordinateDiff(long1, lat1, long2, lat2):
        # Find distance between two coordinates
        # Haversine formula
        R = 6371
        d_lat = math.radians((lat2-lat1))
        d_long = math.radians((long2-long1))
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)
        a = math.sin(d_lat/2)**2 +
            math.sin(d_long/2)**2 * math.cos(lat1) * math.cos(lat2)
        c = 2 * math.atan2(math.sqrt(a), math/sqrt(1-a))
        distance = R * c
        return distance

    @staticmethod
    def IPGeolocate(IP):
        # Get data about IP address and parse it to extract city and country.
        # Translate city and country into longitude and latitude coordinates.
        raw_data = getGeody(IP)
        # countries = list(getCountries())
        city_country = cityCountryParser(raw_data)
        print(city_country)
        if "UNKNOWN" in normalizeWhitespace(city_country):
            return -80, -100
        latitude, longitude = latLong(city_country)
        return latitude, longitude
    
    @staticmethod
    def IPDistance(IP1, IP2):
        # Given two IP addresses, find distance between these in real life
        lat1, long1 = IPGeolocate(IP1)
        lat2, long2 = IPGeolocate(IP2)
        distance = coordinateDiff(long1, lat1, long2, lat2)
        return distance



    @staticmethod
    def locatePerfSonarInstances(ISO_3166CountryCode, perfSonarProjectName):
        matchingCountryPerfSonarList = []
        perfSonarAccessor = PerfSonarAccessor.PerfSonarAccessor(perfSonarProjectName)
        perfSonarResources = perfSonarAccessor.getProjectSiteList()

        for perfSonarResource in perfSonarResources:
            isIp = re.match("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$", perfSonarResource)
            #print perfSonarResource
            if isIp:
                currentIP = perfSonarResource
            else:
                try:
                    currentIP = socket.gethostbyname(perfSonarResource)
                except:
                    continue
                    #currentIP = socket.getaddrinfo(perfSonarResource, None, socket.AF_INET6)
                    #print socket.getfqdn(currentIP)


            currentISO_3166_1_ALPHA_2_CountryCode = LarkUtilities.ISO_3166_1_ALPHA_2_IpAddressGeoLocate(currentIP)
            tempTouple = (perfSonarResource, currentISO_3166_1_ALPHA_2_CountryCode)
            #print tempTouple
            if currentISO_3166_1_ALPHA_2_CountryCode == None:
                continue
            if currentISO_3166_1_ALPHA_2_CountryCode[0] == None:
                continue
            #print ISO_3166CountryCode.lower() + " = " + currentISO_3166_1_ALPHA_2_CountryCode[0].lower() + " : " + ISO_3166CountryCode.lower() == currentISO_3166_1_ALPHA_2_CountryCode[0].lower()
            if ISO_3166CountryCode.lower() == currentISO_3166_1_ALPHA_2_CountryCode[0].lower():
                matchingCountryPerfSonarList.append(tempTouple)
        
        print perfSonarResources
        #print matchingCountryPerfSonarList
        return matchingCountryPerfSonarList

   
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
