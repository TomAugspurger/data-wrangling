import urllib2

from bs4 import BeautifulSoup
import pandas as pd
import lxml
import xml_parse


# On Disk Example

path = 'Comtrade.xml'  # Located on disk.
soup = BeautifulSoup(open(path), 'lxml')
tag = soup.r
names = []
dictionary = xml_parse.get_names(tag, names)
df = xml_parse.to_frame(soup, dictionary)


############ From the Web ############

"""
xml = 'http://comtrade.un.org/ws/'
xmlpath = 'get.aspx?cc=TOTAL&px=H2&r=372&y=2006&comp=false&code='
access_code = '0+eQr1v/Ipy4z+k0Gbpgb7uR4roBFhizAELaCTsNqaRbSu5koYjlZSXNnj01'+\
	'N5Jq+qM/zN43pjkOtPV8EM1bi7p3JHZH7G221VQUoqJx0QO+LZ2QtYWVJ9tTgriP0b358h'+\
	'nSlo7DqWSizp4J1bIj6Mw9NQe5Pa85q6636s62AIA='

soup = BeautifulSoup(urllib2.urlopen(
        xml + xmlpath + access_code), 'lxml')
"""