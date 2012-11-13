import os
from cPickle import load

import numpy as np
import pandas as pd
from weighting_matrix import weight_matrix as wm


os.chdir('/Volumes/HDD/Users/tom/DataStorage/Comext/yearly')

with open('years_dict.pkl', 'r') as years_dict_file:
    years_dict = load(years_dict_file)
years_dict_file.closed
years = sorted(years_dict.keys())


def flip(x):
    if x == 1:
        return 2
    else:
        return 1

def error(w, s, store, country, product, partner, year, reference, flow):
    """
    u_gct = [delta^k * ln(p_gct)]**2 - theta_1 * (delta^k * ln(s_gct))**2 -
        theta_2 * (delta^k * ln(p_gct) * delta^k * ln(s_gct))

    Where
        theta_1 = w_g / ((1 + w_g)(sigma_g - 1))
        theta_2 = (1 - w_g(sigma_g - 2)) / ((1 + w_g)(sigma_g -1))

    Parameters:
    -----------
    s : the elasticity of substitution for that variety
    w : omega, inverse supply elasticity


    # TODO:
    # Build in some error control for if no ref in EuroArea.  May want
    # to avoid the EU group btw.
    ------------------------
    I'm temporarily assuming that when we difference with country k, we're
    looking at the **exports** of country k, when the country of focus in
    **importing**.  This means the (log) diff with country k will be about
    zero.
    """

    y0 = years[years.index(year) - 1]

    share = np.log(store[year + '_' + country]['VALUE_1000ECU'].xs((flow, product, partner),
        level=('FLOW', 'PRODUCT_NC', 'PARTNER')) / (
        store[year + '_' + country]['VALUE_1000ECU'].xs((flow, product),
        level=('FLOW', 'PRODUCT_NC'))['VALUE_1000ECU'].sum())) - (
        np.log(store[y0 + '_' + country])['VALUE_1000ECU'].xs((flow, product, partner),
        level=('FLOW', 'PRODUCT_NC', 'PARTNER')) / (
        store[y0 + '_' + country]['VALUE_1000ECU'].xs((flow, product),
        level=('FLOW', 'PRODUCT_NC'))['VALUE_1000ECU'].sum())) - (
        np.log(store[year + '_' + country]['VALUE_1000ECU'].xs((flip(flow), product, partner),
        level=('FLOW', 'PRODUCT_NC', 'PARTNER')) / (
        store[year + '_' + country]['VALUE_1000ECU'].xs((flip(flow), product),
        level=('FLOW', 'PRODUCT_NC'))['VALUE_1000ECU'].sum())) - (
        np.log(store[y0 + '_' + country])['VALUE_1000ECU'].xs((flip(flow), product, partner),
        level=('FLOW', 'PRODUCT_NC', 'PARTNER')) / (
        store[y0 + '_' + country]['VALUE_1000ECU'].xs((flip(flow), product),
        level=('FLOW', 'PRODUCT_NC'))['VALUE_1000ECU'].sum())) 
        )
        
        

    price = store[year + '_price_' + country].xs((flow, product, partner), 
        level = ('FLOW', 'PRODUCT_NC', 'PARTNER')) #PARTNER? Self?

    u = 

    # prices = (np.log(store[year + '_' + 'price' + '_' + country].xs(
    #     (years_dict[year], product), level=('PERIOD', 'PRODUCT_NC'))) -
    #     np.log(store[year + '_' + 'price' + '_' + reference].xs(
    #     (years_dict[year], product), level=('PERIOD', 'PRODUCT_NC')))) ** 2

    # # ((price * quantity) of variety) / (total exp on that product.)
    # shares = (np.log(store[year + '_price' + country].xs((product, partner),
    #     level=('PRODUCT_NC', 'PARTNER'))) * (
    # store['quantity_' + country].xs((product, partner))))

    

    # ASSUME A REFERENCE COUNTRY


def get_reference(store, country,
        years=['y2007', 'y2008', 'y2009', 'y2010', 'y2011']):
    """
    Finds potential countries to use as k in calculating errors.
    Must provide a positive quantity in every year. (Exports & Imports?)

    Read inside out to maintain sanity.  Would be so easy recursively...
        Get index wm for first year possible (i.e. second year in sample).
        Filter by calling .ix on that index; drop the NaNs.  Take that index.
        ...
        End with index of (flow, product, partner) that works as references.

    TODO:
    Going to have to rework this to return a list of potentials for each product.
    From that list we'll (automatically according to some criteria) choose
    the reference **for that product**.  That criteria MUST include preference
    for other countries in the dataset.  If not, no way to calculate moment.

    Parameters:
    -----------
    store : HDF5Store
    country : String
    years: list of strings

    Returns:
    --------
    DataFrame (call index on this; for storage reasons)
    """

    return wm(store, country, years[4]).ix[
        wm(store, country, years[3]).ix[
        wm(store, country, years[2]).ix[
        wm(store, country, years[1]).index
        ].dropna().index
        ].dropna().index
        ].dropna()
