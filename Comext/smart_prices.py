import os
from cPickle import load
from datetime import datetime

import numpy as np
import pandas as pd
from get_reference2 import get_reference

os.chdir('/Volumes/HDD/Users/tom/DataStorage/Comext/yearly')
yearly = pd.HDFStore('yearly.h5')


def get_prices(country, year, square=2, store=yearly):
    """
    Use to fill prices for gmm calc.

    Parameters
    --------

    Returns
    -------
    A dataframe w/ col name p_YYYY
    """

    year1 = 'y' + str(year) + '_'
    year0 = 'y' + str(year - 1) + '_'
    iyear1 = int(str(year) + '52')
    iyear0 = int(str(year - 1) + '52')

    df1 = yearly[year1 + 'price_' + country][0].ix[1]  # Need [0] to get Series.
    df0 = yearly[year0 + 'price_' + country][0].ix[1]

    df1.name = 'p' + str(year)
    df0.name = 'p' + str(year - 1)

    gr1 = df1.groupby(axis=0, level='PRODUCT_NC')
    gr0 = df0.groupby(axis=0, level='PRODUCT_NC')

    l1 = []
    drops1 = []
    for product in gr1.groups.keys():
        try:
            l1.append((iyear1, product, ref_dict[product]))
        except KeyError:
            drops1.append(product)

    l0 = []
    drops0 = []
    for product in gr0.groups.keys():
        try:
            l0.append((iyear0, product, ref_dict[product]))
        except KeyError:
            drops0.append(product)

    return pd.DataFrame((np.log(df1.ix[iyear1]) - np.log(df0.ix[iyear0]) - (
            np.log(df1.ix[l1].ix[iyear1].reset_index(level='PARTNER')['p' + str(year)].reindex(df1.index, level='PRODUCT_NC').ix[iyear1]) - (
            np.log(df0.ix[l0].ix[iyear0].reset_index(level='PARTNER')['p' + str(year - 1)].reindex(df0.index, level='PRODUCT_NC').ix[iyear0])))), columns=['p_' + str(year)]) ** square


start_time = datetime.now()
os.chdir('/Volumes/HDD/Users/tom/DataStorage/Comext/yearly')

# Globals

yearly = pd.HDFStore('yearly.h5')
gmm_store = pd.HDFStore('gmm_store.h5')
with open('declarants_no_002_dict.pkl', 'r') as f:
    declarants = load(f)
f.closed
years = [2007, 2008, 2009, 2010, 2011]

# Processing
# Need to merge the first one too.
for country in sorted(declarants):
    ref_dict = get_reference(yearly, country)
    for year in years[1:]:
        print 'Working on %r, %r.' % (country, year)
        print datetime.now() - start_time
        gmm_store['s_' + country] = gmm_store['ps_' + country].merge(
            get_prices(country, year),
            how='outer', left_index=True, right_index=True)

##############################################################################
# os.chdir('/Volumes/HDD/Users/tom/DataStorage/Comext/yearly')
# yearly = pd.HDFStore('yearly.h5')
# country = '001'

# df07 = yearly['y2007_price_001'][0].head(500).ix[1]  # Need [0] to get Series.
# df08 = yearly['y2008_price_001'][0].head(500).ix[1]

# df07.name = 'p2007'
# df08.name = 'p2008'

# gr07 = df07.groupby(axis=0, level='PRODUCT_NC')
# gr08 = df08.groupby(axis=0, level='PRODUCT_NC')

# ref_dict = get_reference(yearly, country)


# l1 = gr08.groups.keys()
# l2 = []
# drops08 = []
# for product in l1:
#     try:
#         l2.append((200852, product, ref_dict[product]))
#     except KeyError:
#         drops08.append(product)

# l3 = gr07.groups.keys()
# l4 = []
# drops07 = []
# for product in l3:
#     try:
#         l4.append((200752, product, ref_dict[product]))
#     except KeyError:
#         drops07.append(product)

# ydiff = np.log(df08.ix[200852]) - np.log(df07.ix[200752])

# kdiff = np.log(df08.ix[l2].ix[200852].reset_index(level='PARTNER')['p2008'].reindex(df08.index, level='PRODUCT_NC').ix[200852]) - (
#         np.log(df07.ix[l4].ix[200752].reset_index(level='PARTNER')['p2007'].reindex(df07.index, level='PRODUCT_NC').ix[200752]))

# x = ydiff - kdiff

