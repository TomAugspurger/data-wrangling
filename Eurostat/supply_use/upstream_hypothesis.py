from __future__ import division

from cPickle import load

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# USE Table
"""
*Classification Notes*:
    -Should be by NACE Rev. 2.
Might actually be what LLT call downstream.
"""


class use(object):
    """Class for readying data for upstream hypothesis.  See Levchencko,
    Lewis, and Tesar p. 13/14 for more.
    """
    def __init__(self):
        super(use, self).__init__()
        with open('/Users/tom/TradeData/data-wrangling/Eurostat/supply_use/'\
            'docs/clean_use_row_labels.pkl', 'r') as f:
            self.d_row = load(f)

        with open('/Users/tom/TradeData/data-wrangling/Eurostat/supply_use/'\
            'docs/clean_use_col_labels.pkl', 'r') as f:
            self.d_col = load(f)

        with open('/Users/tom/TradeData/data-wrangling/correspondences/cpa-cn/'\
            'cpa-cn_dict.pkl', 'r') as f:
            self.d_cpa_cn = load(f)

        self.remove = {
            'P3': 'Final consumption expenditure',
            'P3_S13': 'Final consumption expenditure by government',
            'P3_S14': 'Final consumption expenditure by households',
            'P3_S15': 'Final consumption expenditure by non-profit '\
                'organisations serving households (NPISH)',
            'P5': 'Gross capital formation',
            'P51': 'Gross fixed capital formation',
            'P52': 'Changes in inventories',
            'P52_P53': 'Changes in inventories and valuables',
            'P53': 'Changes in valuables',
            'P6': 'Exports',
            'P6_S21': 'Exports intra EU fob',
            'P6_S2111': 'Exports of goods and services EMU members (fob)',
            'P6_S2112': 'Exports of goods and services to EMU non-members (fob)',
            'P6_S22': 'Exports extra EU fob',
            'TFINU': "Final use at purchasers'prices",
            'TOTAL': 'Total',
            'TU': "Total use at purchasers' prices"
            }

        df = pd.read_csv('/Users/tom/TradeData/data-wrangling/Eurostat/'\
            'supply_use/tables/clean_naio_cp16_r2.csv',
            index_col=['unit', 'geo', 'cols', 'rows'])
        df = df.ix['MIO_NAC']
        self.df = df['2008'].unstack(level='cols')

        # Control measure 1: Average value of Downstream use.
        self.res1 = self.df[self.df.columns - self.df[
            self.remove.keys()].columns].mean(axis=1)

        # Control measure 2: Count value of Downstream use.
        def mycount(x):
            return np.count_nonzero(x.dropna())

        self.res2 = self.df[self.df.columns - self.df[
            self.remove.keys()].columns].T.apply(mycount)

        self.thin = [
            'A01',
            'A02',
            'A03',
            'B',
            'C10-C12',
            'C13-C15',
            'C16',
            'C17',
            'C18',
            'C19',
            'C20',
            'C21',
            'C22',
            'C23',
            'C24',
            'C25',
            'C26',
            'C27',
            'C28',
            'C29',
            'C30',
            'C31_C32',
            'C33',
            'D35',
            'E36',
            'E37-E39',
            'F',
            'G45',
            'G46',
            'G47',
            'H49',
            'H50',
            'H51',
            'H52',
            'H53',
            'I',
            'J58',
            'J59_J60',
            'J61',
            'J62_J63',
            'K64',
            'K65',
            'K66',
            'L68A',
            'L68B',
            'M69_M70',
            'M71',
            'M72',
            'M73',
            'M74_M75',
            'N77',
            'N78',
            'N79',
            'N80-N82',
            'O84',
            'P3_S13',
            'P3_S14',
            'P3_S15',
            'P51',
            'P52',
            'P53',
            'P6_S2111',
            'P6_S2112',
            'P6_S22',
            'P85',
            'Q86',
            'Q87_Q88',
            'R90-R92',
            'R93',
            'S94',
            'S95',
            'S96',
            'T',
            'U']

        self.letter_header = {
            'A': ['01', '02', '03'],
            'B': ['05', '06', '07', '08', '09'],
            'C': ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                '20', '21', '22', '23', '24', '25', '26', '27', '28', '29',
                '30', '31', '32', '33'],
            'D': ['35'],
            'E': ['36', '37', '38', '39'],
            'F': ['41', '42', '43'],
            'G': ['45', '46', '47'],
            'H': ['49', '50', '51', '52'],
            'I': ['55', '56'],
            'J': ['58', '59', '60', '61', '62', '63'],
            'K': ['64', '65', '66'],
            'L': ['68'],
            'M': ['69', '70', '71', '72', '73', '74', '75'],
            'N': ['77', '78', '79', '80', '81', '82'],
            'O': ['84'],
            'P': ['85'],
            'Q': ['86', '87', '88'],
            'R': ['90', '91', '92', '93'],
            'S': ['94', '95', '96'],
            'T': ['97', '98'],
            'U': ['99']
            }

    def gen_cn(self, ctry='all'):
        """Use to take values from res1 and broadcast to CN.
        """
        # No data for 'EE' and 'MK'; 'IE' has some more NaNs.
        import sys
        sys.path.append('/Users/tom/TradeData/data-wrangling/correspondences/')
        from cpa_cn_parse import use_col_parse
        if ctry == 'all':
            return (use_col_parse(self, country) for country in
                self.df.index.levels[0].drop(['EE', 'MK']))
        else:
            if type(ctry) == str:
                try:
                    return use_col_parse(self, ctry)
                except:
                    assert 'error'
            elif type(ctry) == list:
                for i, country in enumerate(ctry):
                    try:
                        return use_col_parse(self, country)
                    except:
                        print('No plot for %s') % country
            else:
                print("Check your country type.  Should be str or list.")

    def heatmap(self, a=4, cmap=plt.cm.gray_r, ctry='all'):
        """Returns a plot showing the intensity of a good's use in
        the other axis' industries.

        Parameters:
        df: dataframe (see notes below)
        a: Thinning paramets.  Plots a label for every ath item.
        cmap: colormap

        Call like:
        for country in df.index.levels[0]:
        try:
            heatmap(np.log(df.ix[country]))
        except:
            pass
        """
        import sys
        sys.path.append('/Users/tom/TradeData/data-wrangling/Eurostat/supply_use/')
        from heatmap import hm

        if ctry == 'all':
            for country in self.df.index.levels[0]:
                try:
                    hm(np.log(self.df.ix[country][self.thin]))
                except:
                    print 'No plot for %s' % country
        else:
            if type(ctry) == str:
                try:
                    hm(np.log(self.df.ix[ctry]))
                except:
                    assert 'error'
            elif type(ctry) == list:
                for i, country in enumerate(ctry):
                    try:
                        hm(np.log(self.df.ix[country][self.thin]))
                    except:
                        print('No plot for %s') % country
            else:
                print("Check your country type.  Should be str or list.")
        pass
