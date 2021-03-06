"""
This file generates the unit prices to be used in the GMM computation.

Note that for now we're only considering imports (flow=1), and
the stat-regime of 4 (largest coverage).
"""
#-----------------------------------------------------------------------------
import numpy as np
import pandas as pd
#-----------------------------------------------------------------------------


def unit_price(x):
    """
    Calculate the unit price of a variety, given that row of the
    multi-indexed dataframe.
    """
    if x['quantity'] > 0.0:
        return x['value'] / x['quantity']
    else:
        return np.nan


def gen_shares(x, sums):
    """
    Calculate the import share of a good via the formula:

        s_{i,t}(I) = p_{i,t}x_{i,t} / \sum_{i \in I} p_{i,t}x_{i,t}
    See Feenstra (1994) p. 158. or Broda and Weinstein (2006).
    Note: I *think* that this wants and individual variety's expenditure
    value as a share of expenditure *on that **good**,* at time t.

    Parameters:
    -----------
    x: A row of a dataframe. Called via apply(axis=1)
    sums: A series containing the sums for each good.  Should be indexed like
        period, good.

    Returns
    -------
    That varieties share. Float.
    """
    year, _, good, _ = x.name  # apply appends name to each row.
    return x['value'] / sums.ix[year, good]

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    # Commented out lines are from my previous iteration through.
    # This script has side effects, it modifies the dataframe in place.
    in_store = pd.HDFStore('/Volumes/HDD/Users/tom/DataStorage/Comext/yearly'
                           '/by_declarant.h5')

    out_store = pd.HDFStore('/Volumes/HDD/Users/tom/DataStorage/Comext/yearly'
                            '/filtered_by_declarant.h5')

    items = in_store.iteritems()
    for tup in items:
        name = tup[0].lstrip('/')
        print('Working on {}'.format(name))
        # >1000 are aggregates.
        df = in_store.select(name, [pd.Term('partner < 1000')])
        # Clean up your index.
        df.index = df.index.droplevel(level=['flow', 'stat'])
        df['period'] = df['period'].apply(lambda x: int(str(x)[:4]))
        df = df.set_index(['period', 'declarant', 'good', 'partner'])

        #----------------------------------------------------------------------
        # Prices:  If just using quantity, do here.
        # df['price'] = df.apply(unit_price, axis=1)
        df['price'] = df['value'] / df['quantity']
        df['price'][df['price'] == np.inf] = np.nan  # zero division

        sums = df['value'].groupby(level=('period', 'good')).sum()
        df['share'] = df.apply(gen_shares, axis=1, args=[sums])

        # TODO: Find out if pytables supports appending a column.
        try:
            out_store.remove(name)
            out_store.append(name, df)
        except:
            with open('/Volumes/HDD/Users/tom/DataStorage/Comext/yearly/'
                      'failures.txt', 'a') as f:
                f.write('Failed during removal/adding of {}'.format(name))
