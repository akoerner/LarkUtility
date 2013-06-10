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
import urllib2
import BeautifulSoup

usage = "Run the script: ./IP_Distance.py IPAddress1"

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
    return city_txt


# Script starts
if len(sys.argv)!=2:
    print(usage)
    sys.exit(0)
else:
    IP = sys.argv[1]

raw_data = getGeody(IP)
city_country = cityCountryParser(raw_data)
print(city_country)
