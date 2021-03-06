from __future__ import division

import os
import pandas as pd

"""
may want df.ix[(1, year):(2, year)]
"""

os.chdir('/Volumes/HDD/Users/tom/DataStorage/Comext/yearly')
yearly = pd.HDFStore('yearly.h5')

country_code = {
            '001': 'France',
            '002': 'Belg.-Luxbg',
            '003': 'Netherlands',
            '004': 'Fr Germany',
            '005': 'Italy',
            '006': 'Utd. Kingdom',
            '007': 'Ireland',
            '008': 'Denmark',
            '009': 'Greece',
            '010': 'Portugal',
            '011': 'Spain',
            '017': 'Belgium',
            '018': 'Luxembourg',
            '030': 'Sweden',
            '032': 'Finland',
            '038': 'Austria',
            '600': 'Cyprus',
            '061': 'Czech Republic',
            '053': 'Estonia',
            '064': 'Hungary',
            '055': 'Lithuania',
            '054': 'Latvia',
            '046': 'Malta',
            '060': 'Poland',
            '091': 'Slovenia',
            '063': 'Slovakia',
            '068': 'Bulgaria',
            '066': 'Romania',
            'EU': 'EU',
}

keys = sorted(country_code.keys())

# for leaf in yearly.keys():
#     for key in keys:
#         try:
#             yearly[leaf + key] = yearly[leaf].xs(key, level='DECLARANT')
#             print 'done with %s, %s' % (leaf, key)
#         except:
#             print 'Trouble with %s, %s' % (leaf, key)
#     print 'All done with %s' % leaf

"""
Notes on how that went:
Failers on all the prices.
Failers also on:
    Trouble with y2007, 001
    Trouble with y2007, 002
    Trouble with y2007, 003
    Trouble with y2011, 002
    Trouble with y2010, 002
    Trouble with y2008, 002
    Trouble with y2009, 002

2007 001, 002, and 003 should have worked.
    I may have messed them up with ctrl-c's.

'002' : Belg.-Lux may just be zeros.
On to prices:
    Idiot.  Series don't have .xs.
    Idiot.  Forgot comma in todo.
"""
todo = [
    'y2007001',
    'y2007003'
]
# Very hackish with the -5: slice to get the prices.

# for leaf in yearly.keys():
#     for key in keys:
#         if leaf + key in todo:
#             try:
#                 yearly[leaf + '_' + key] = yearly[leaf].xs(key, level='DECLARANT')
#                 print 'done with %s, %s' % (leaf, key)
#             except:
#                 print 'Trouble with %s, %s' % (leaf, key)
#         else:
#             pass
#     print 'All done with %s' % leaf

for leaf in yearly.keys():
    for key in keys:
        if leaf[-5:] == 'price':
            try:
                yearly[leaf + '_' + key] = pd.DataFrame(yearly[leaf]).xs(
                    '001', level='DECLARANT')
                print 'done with %s, %s' % (leaf, key)
            except:
                print 'Trouble with %s, %s' % (leaf, key)
        else:
            pass

yearly.close()
