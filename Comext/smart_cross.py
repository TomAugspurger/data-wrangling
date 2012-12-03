from __future__ import division

import os
from cPickle import load
from datetime import datetime

import numpy as np
import pandas as pd


start_time = datetime.now()
os.chdir('/Volumes/HDD/Users/tom/DataStorage/Comext/yearly')

yearly = pd.HDFStore('yearly.h5')
gmm_store = pd.HDFStore('gmm_store.h5')

with open('declarants_no_002_dict.pkl', 'r') as f:
    declarants = load(f)
f.closed

with open('references_dict.pkl', 'r') as f:
    ref_dict_all = load(f)


years = [2007, 2008, 2009, 2010, 2011]


def get_shares(country, year, square=2, name='s_', store=yearly):
    """
    Use to fill in the table for gmm calculation.

    Parameters
    ----------
    country : string.  Probably from an outer loop.
    year : int.
    square : whether to square the result or not. Defaults to true (i.e. 2).
    name : string. For the returned column name.
    store : HDFStore.
    Returns
    -------
    A dataframe w/ col name name_YYYY
    """

    year1 = 'y' + str(year) + '_'
    year0 = 'y' + str(year - 1) + '_'
    iyear1 = int(str(year) + '52')
    iyear0 = int(str(year - 1) + '52')

    df1 = yearly[year1 + country]['VALUE_1000ECU'][yearly[year1 + country]['STAT_REGIME'] == 4].ix[1]
    df0 = yearly[year0 + country]['VALUE_1000ECU'][yearly[year0 + country]['STAT_REGIME'] == 4].ix[1]

    gr1 = df1.groupby(axis=0, level='PRODUCT_NC')
    gr0 = df0.groupby(axis=0, level='PRODUCT_NC')

    l1 = []
    drop1 = []
    for product in gr1.groups.keys():
        try:
            l1.append((iyear1, product, ref_dict[product]))
        except KeyError:
            drop1.append(product)

    l0 = []
    drop0 = []
    for product in gr0.groups.keys():
        try:
            l0.append((iyear0, product, ref_dict[product]))
        except KeyError:
            drop0.append(product)

    # Check if return is actually what you want to do.
    return pd.DataFrame(
        np.log(df1 / gr1.sum().reindex(df1.index, level='PRODUCT_NC')).ix[iyear1] - (
        np.log(df0 / gr0.sum().reindex(df0.index, level='PRODUCT_NC')).ix[iyear0]) - (
        np.log(df1.ix[l1].ix[iyear1].reset_index(level='PARTNER')['VALUE_1000ECU'].reindex(df1.index, level='PRODUCT_NC').ix[iyear1] / gr1.sum().reindex(df1.index, level='PRODUCT_NC').ix[iyear1]) - (
        np.log(df0.ix[l0].ix[iyear0].reset_index(level='PARTNER')['VALUE_1000ECU'].reindex(df0.index, level='PRODUCT_NC').ix[iyear0] / gr0.sum().reindex(df0.index, level='PRODUCT_NC').ix[iyear0])
        )
        ), columns=[name + str(year)]
        ) ** square


def get_prices(country, year, square=2, name='p_', store=yearly):
    """
    Use to fill prices for gmm calc.

    Parameters
    --------
    country : string.  Probably from an outer loop.
    year : int.
    square : whether to square the result or not. Defaults to true (i.e. 2).
    name : string. For the returned column name.
    store : HDFStore.
    Returns
    -------
    A dataframe w/ col name name_YYYY
    """

    year1 = 'y' + str(year) + '_'
    year0 = 'y' + str(year - 1) + '_'

    df1 = yearly[year1 + 'price_' + country]
    df0 = yearly[year0 + 'price_' + country]

    df1.name = 'p' + str(year)
    df0.name = 'p' + str(year - 1)

    gr1 = df1.groupby(axis=0, level='PRODUCT_NC')
    gr0 = df0.groupby(axis=0, level='PRODUCT_NC')

    l1 = []
    drops1 = []
    for product in gr1.groups.keys():
        try:
            l1.append((product, ref_dict[product]))
        except KeyError:
            drops1.append(product)

    l0 = []
    drops0 = []
    for product in gr0.groups.keys():
        try:
            l0.append((product, ref_dict[product]))
        except KeyError:
            drops0.append(product)

    return pd.DataFrame((np.log(df1) - np.log(df0) - (
            np.log(df1.ix[l1].reset_index(level='PARTNER')['p' + str(year)].reindex(df1.index, level='PRODUCT_NC')) - (
            np.log(df0.ix[l0].reset_index(level='PARTNER')['p' + str(year - 1)].reindex(df0.index, level='PRODUCT_NC'))))), columns=[name + str(year)]) ** square


for country in sorted(declarants):
    ref_dict = ref_dict_all[country]
    for year in years[1:]:
        print 'Working on %r, %r.' % (country, year)
        print(datetime.now() - start_time)
        if year == 2008:
            gmm_store['c_' + country] = (
                get_shares(country, year, square=1, name=('c_')) *
                get_prices(country, year, square=1, name=('c_'))
                )
        else:
            gmm_store['c_' + country] = gmm_store['c_' + country].merge(
                get_shares(country, year, square=1, name=('c_')) *
                get_prices(country, year, square=1, name=('c_')),
                how='outer', left_index=True, right_index=True)