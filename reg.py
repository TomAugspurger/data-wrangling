from __future__ import division

import sys
import datetime as dt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm

sys.path.append('/Users/tom/TradeData/data-wrangling/correspondences')
sys.path.append('/Users/tom/TradeData/data-wrangling/Eurostat/response')
from response import pct_chng
from durables_classification import get_dummy


monthly = pd.HDFStore('/Volumes/HDD/Users/tom/DataStorage/Comext/monthly.h5')
yearly = pd.HDFStore('/Volumes/HDD/Users/tom/DataStorage/Comext/yearly/yearly.h5')
# Most drops in 2008Q2, next most in 2008Q3


def just_8(df):
    """Filters out the aggregates, leaving only 8 digit indicies.
    Expects df to have index level 1 of products.
    """
    if df.index.levels[0].name != 'PRODUCT_NC':
        raise NameError
    return df.index.levels[0][[len(x) == 8 for x in df.dropna().index.levels[0]]]


class grandRegression(object):
        """docstring for grad_reg"""
        def __init__(self, country, date):
            """Date should be [int, int], [year, month].
            Country should be from Comext, e.g. '001'.
            """
            super(grandRegression, self).__init__()
            from cPickle import load
            with open('/Users/tom/TradeData/data-wrangling/correspondences/'\
                'country_names_dict.pkl', 'r') as f:
                country_dict = load(f)
            with open('/Users/tom/TradeData/data-wrangling/correspondences/'\
                'country_abbvr_dict.pkl', 'r') as f:
                country_abbvr = load(f)
            self.m_dict = {
                1: ['jan', 1], 2: ['feb', 1], 3: ['mar', 1], 4: ['apr', 2],
                5: ['may', 2], 6: ['jun', 2], 7: ['jul', 2], 8: ['aug', 2],
                9: ['sep', 2], 10: ['oct', 4], 11: ['nov', 4], 12: ['dec', 4]
                }
            self.country = country
            self.country_name = country_dict[self.country]
            self.country_abbvr = country_abbvr[self.country]
            self.int_country = int(self.country)  # Wont work for EU
            self.month = self.m_dict[date[1]][0]  # str
            self.q = self.m_dict[date[1]][1]
            self.year = date[0]
            self.yearly = 'y' + str(self.year) + '_' + self.country
            self.isodt = dt.datetime.isoformat(dt.datetime(
                self.year, date[1], 1))[:10]

            #Data IO
            self.df = monthly[self.month + '_' + str(self.year)[2:]].xs((
                1, self.isodt, self.int_country, 4), level=('FLOW', 'PERIOD',
                'DECLARANT', 'STAT_REGIME'))
            self.sf = yearly[self.yearly][yearly[self.yearly][
            'STAT_REGIME'] == 4].xs((1, int(str(self.year) + '52')), level=("FLOW", 'PERIOD'))
            self.y = pct_chng(self.int_country, [self.year, self.q]).dropna()

            # Indicies
            self.idx8 = just_8(self.df)

            # Size of each product relative to ALL imports.
            self.df_red = pd.DataFrame(self.df.ix[self.idx8].groupby(axis=0,
                level='PRODUCT_NC')['VALUE_1000ECU'].sum() / (self.df.ix[
                self.idx8].groupby(axis=0, level='PRODUCT_NC')[
                'VALUE_1000ECU'].sum().sum()), columns=['size'])

            get_dummy(self.df_red)
            self.df_red = sm.add_constant(self.df_red, prepend=True)

            self.idx = self.y.index.intersection(self.df_red.dropna().index)
            self.endog = self.y[self.y != np.inf][self.idx]
            self.endog.name = 'pct_change'
            self.exog = self.df_red.ix[self.idx]

        def get_labor(self):
            """Get a df for labor controls.
            """
            sys.path.append('/Users/tom/data-wrangling/Eurostat/labor_input')
            import cPickle
            from nace_cn_parse import get_val
            with open('/Users/tom/Tradedata/data-wrangling/correspondences/'\
                'cpa-cn/cpa-cn_dict.pkl', 'r') as f:
                d_cpa_cn = cPickle.load(f)

            self.exog['labor'] = get_val(pd.read_csv('/Users/tom/TradeData/'\
                'data-wrangling/Eurostat/labor_input/labor_input_00to06_'\
                'clean.csv', index_col=['geo', 'nace']), self.country_abbvr)
            print('Added labor input to self.exog!')

        def estimate(self, args, winsor=False):
            """Get fitted regression result.  No controls for now.
            args is a list of column names for the included variables.
            If winsor, replace outliers with 3 sigma.
            """
            # if winsor:
            #     sys.path.append('/Users/tom/TradeData/data-wrangling/')
            #     from winsor import winsorize
            #     y = winsorize(self.endog)
            #     x = winsor(self.exog)
            # else:
            #     y = self.endog
            #     x = self.exog

            idx = self.endog.index.intersection(self.exog[args].dropna(
                how='any').index)
            model = sm.OLS(self.endog[idx], self.exog[args].ix[idx])
            return model.fit()

        def my_filter(self, on=['all'], q=.9):
            """Attempt to "deal with" (ignore) outliers.
            q is a list of quantiles.
            """
            d = {}
            all_columns = [self.endog.name] + self.exog.columns.tolist()
            if on == ['all']:
                columns = all_columns
            else:
                columns = on

            for col in columns:
                if col == 'const' or col == 'durable':
                    print col
                    d[col] = self.exog[col]
                elif col == 'pct_change':
                    d[col] = self.endog[self.endog <
                        self.endog.quantile(q)]
                else:
                    try:
                        d[col] = self.exog[col][self.exog[col] <
                            self.exog[col].quantile(q)]
                    except:
                        print 'messed up %s' % col
            for col in set(all_columns) - set(columns):
                if col == 'pct_change':
                    d[col] = self.endog
                else:
                    d[col] = self.exog[col]
            df = pd.DataFrame(d)
            f_idx = df.dropna(how='any').index
            df = df.ix[f_idx]

            self.f_exog = self.exog.ix[f_idx]
            self.f_endog = self.endog[f_idx]

        def upstream(self, method='res1'):
            """Use to test upstream hypothesis.
            Methods can be res1 or res2.
            """
            sys.path.append('/Users/tom/TradeData/data-wrangling/'\
                'Eurostat/supply_use/')
            from upstream_hypothesis import use
            c = use()
            df = c.gen_cn(ctry=self.country_abbvr)
            id1 = df.index
            id2 = self.endog.index
            idx = id1.intersection(id2)  # Note: temporary.  Differs from above

            return df.ix[idx].join(self.endog[idx]).join(self.exog.ix[idx]).dropna()

if __name__ == '__main__':
    c = grandRegression('001', [2008, 6])

# Testing
"""
df = monthly['sep_09'].xs((1, '2009-09-01'), level=('FLOW', 'PERIOD'))
sf = yearly['y2009_001']
sf = sf[sf['STAT_REGIME'] == 4].xs((1, 200952), level=("FLOW", 'PERIOD'))
gr = sf.groupby(axis=0, level='PRODUCT_NC')

y = pct_chng('001', [2009, 3]).dropna().ix[1]

test = df.xs(('001', 4), level=("DECLARANT", 'STAT_REGIME'))
res = pd.DataFrame(
    test.groupby(axis=0, level='PRODUCT_NC')['VALUE_1000ECU'].sum())

idx8 = res.index[[len(x) == 8 for x in res.index]]  # Need to avoid partners.
gr2 = test.ix[idx8].groupby(axis=0, level='PRODUCT_NC')
sc = pd.DataFrame(
    gr2['VALUE_1000ECU'].sum()[idx8] / gr2['VALUE_1000ECU'].sum()[idx8].sum())
sc.columns = ['size']
get_dummy(sc)

idx = y.dropna().index.intersection(idx8)
idx4 = idx3.intersection(exog.dropna().index)

endog = y[idx]
exog = sm.add_constant(sc.ix[idx], prepend=True)

model = sm.OLS(y[idx4], exog[['const', 'durable', 'size']].ix[idx4])
results = model.fit()
print results.summary()

### Some plotting ###
y2 = endog[endog < .5]
x2 = exog[exog['size'] < .015]
idx3 = y2.index.intersection(x2.index)
plt.scatter(exog['size'].ix[idx3], endog[idx3])
plt.figure()
plt.subplot(111)
plt.scatter(exog['size'].ix[idx3], endog[idx3])
"""