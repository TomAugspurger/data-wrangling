import cPickle
from itertools import izip

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.covariance import EmpiricalCovariance, MinCovDet
#-----------------------------------------------------------------------------
base = '/Volumes/HDD/Users/tom/DataStorage/Comext/yearly/'
with open(base + 'declarants_no_002_dict.pkl', 'r') as declarants:
    country_code = cPickle.load(declarants)
    declarants = sorted(country_code.keys())

gmm_res = pd.HDFStore('/Volumes/HDD/Users/tom/DataStorage/Comext/yearly/'
                      'gmm_results.h5')

weighted_res = pd.HDFStore('/Volumes/HDD/Users/tom/DataStorage/Comext/yearly/'
                           'gmm_results_weighted.h5')

#-----------------------------------------------------------------------------
# Helper functions


def load_pre(ctry, close=True):
    """
    Get a dataframe with the trade data.
    """
    base = '/Volumes/HDD/Users/tom/DataStorage/Comext/yearly/'
    gmm = pd.HDFStore(base + 'gmm_store.h5')
    df = gmm.select('by_ctry_' + ctry)
    if close:
        gmm.close()
    return df


def load_res(ctry, weighted=True, close=True):
    """
    Get a dataframe with the estimated parameters for that country.
    """
    if weighted:
        gmm_res = pd.HDFStore(base + 'gmm_results_weighted.h5')
    else:
        gmm_res = pd.HDFStore(base + 'gmm_results.h5')
    df = gmm_res.select('res_' + ctry)
    if close:
        gmm_res.close()
    return df


def get_extremes(pre=None, res=None, ctry=None, weighted=True):
    """
    Get the dataframe of price and share who ended up giving
    the max and min values for theta1 and theta2.
    """
    if pre is None:
        try:
            pre = load_pre(ctry)
        except NameError:
            raise NameError('You Need to give a country code')
    if res is None:
        res = load_res(ctry, weighted=weighted)
    maxes = res.idxmax()
    mins = res.idxmin()
    rmax = [pre.xs(maxes[x], level='PRODUCT_NC') for x in maxes.index]
    rmin = [pre.xs(mins[x], level='PRODUCT_NC') for x in mins.index]
    return {'maxes': rmax, 'mins': rmin}


def scatter_(ctry=None, df=None, inliers=False, weighted=True, **kwargs):
    """
    Plot a scatter of the two parameters.  Give either a country code
    or a dataframe of estimated parameters.  If inliers, the dataframe
    will filter out the outliers.
    """
    if df is None and ctry is None:
        raise ValueError('Either the country or a dataframe must be supplied')
    if df is None:
        df = load_res(ctry, weighted=weighted)
    if inliers:
        df = get_inliers(df=df, **kwargs)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(df.t1, df.t2, alpha=.67, marker='.')
    try:
        ax.set_title(country_code[ctry])
    except:
        ax.set_title(ctry)
    return ax


def get_outliers(ctry=None, df=None, s=3, weighted=True, how='any'):
    """
    Find all observations which are at least s (three) sigma for (all)
    or (any) of the features.
    """
    if df is None and ctry is None:
        raise ValueError('Either the country or a dataframe must be supplied')
    if df is None:
        df = load_res(ctry, weighted=weighted)
    if how == 'any':
        return df[(np.abs(df) > df.std()).any(1)]
    elif how == 'all':
        return df[(np.abs(df) > df.std()).all(1)]
    else:
        raise TypeError('how must be "any" or "all".')


def get_inliers(df=None, ctry=None, s=3, weighted=True, how='all'):
    """
    Get a subset of df with just inliers.  When how='any', this is the
    complement to get_outliers with how='all', and vice-versa.
    """
    if df is None and ctry is None:
        raise ValueError('Either the country or a dataframe must be supplied')
    if df is None:
        df = load_res(ctry, weighted=weighted)
    if how == 'any':
        return df[(np.abs(df) <= df.std()).any(1)]
    elif how == 'all':
        return df[(np.abs(df) <= df.std()).all(1)]
    else:
        raise TypeError('how must be "any" or "all".')


def mahalanobis_plot(ctry=None, df=None, weighted=True, inliers=False):
    """
    See http://scikit-learn.org/0.13/modules/outlier_detection.html#\
        fitting-an-elliptic-envelop

    for details.
    """
    if df is None and ctry is None:
        raise ValueError('Either the country or a dataframe must be supplied')
    elif df is None:
        df = load_res(ctry, weighted=weighted)
    if inliers:
        df = get_inliers(df=df)
    X = df.values
    robust_cov = MinCovDet().fit(X)
    #-----------------------------------------------------------------------------
    # compare estimators learnt from the full data set with true parameters
    emp_cov = EmpiricalCovariance().fit(X)
    #-----------------------------------------------------------------------------
    # Display results
    fig = plt.figure()
    fig.subplots_adjust(hspace=-.1, wspace=.4, top=.95, bottom=.05)
    #-----------------------------------------------------------------------------
    # Show data set
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.scatter(X[:, 0], X[:, 1], alpha=.5, color='k', marker='.')
    ax1.set_title(country_code[ctry])
    #-----------------------------------------------------------------------------
    # Show contours of the distance functions
    xx, yy = np.meshgrid(np.linspace(ax1.get_xlim()[0], ax1.get_xlim()[1],
                                     100),
                         np.linspace(ax1.get_ylim()[0], ax1.get_ylim()[1],
                                     100))
    zz = np.c_[xx.ravel(), yy.ravel()]
    #-----------------------------------------------------------------------------
    mahal_emp_cov = emp_cov.mahalanobis(zz)
    mahal_emp_cov = mahal_emp_cov.reshape(xx.shape)
    emp_cov_contour = ax1.contour(xx, yy, np.sqrt(mahal_emp_cov),
                                  cmap=plt.cm.PuBu_r,
                                  linestyles='dashed')
    #-----------------------------------------------------------------------------
    mahal_robust_cov = robust_cov.mahalanobis(zz)
    mahal_robust_cov = mahal_robust_cov.reshape(xx.shape)
    robust_contour = ax1.contour(xx, yy, np.sqrt(mahal_robust_cov),
                                 cmap=plt.cm.YlOrBr_r, linestyles='dotted')
    ax1.legend([emp_cov_contour.collections[1], robust_contour.collections[1]],
               ['MLE dist', 'robust dist'],
               loc="upper right", borderaxespad=0)
    ax1.grid()
    return (fig, ax1, ctry)


def hist_(ctry=None, df=None, ncuts=1000, weighted=True, inliers=False):
    """
    Histogram for a country.  This one is plots t1 and t2 side by side.
    """
    if df is None:
        df = load_res(ctry, weighted=True)
    if inliers:
        df = get_inliers(df=df)
    cuts = np.linspace(min(df.min()), max(df.max()), ncuts)
    cutted = [pd.cut(df.t1, bins=cuts), pd.cut(df.t2, bins=cuts)]
    cutted = [sorted(x) for x in cutted]
    s1, s2 = [pd.DataFrame(pd.value_counts(x, sort=False)) for x in cutted]
    s1.columns = ['t1']
    s2.columns = ['t2']
    joined = s1.join(s2, how='outer', sort=False).fillna(0)
    ax = joined.plot(kind='bar')
    ticks = ax.get_xticks()
    labels = ax.get_xticklabels()
    ticks = ticks[::10]  # Every other.
    labels = labels[::6]
    return ax


def hist_2(ctry=None, df=None, ncuts=1000, weighted=True, thin=4, inliers=False):
    """
    Histogram for a country.  This one is plots t1 and t2 on separate subplots.
    """
    if df is None:
        df = load_res(ctry, weighted=True)
    if inliers:
        df = get_inliers(df=df)
    cuts = [np.linspace(df.min()[x], df.max()[x], ncuts) for x in ['t1', 't2']]
    cutted = [pd.cut(df.t1, bins=cuts[0]), pd.cut(df.t2, bins=cuts[1])]
    # cutted = [sorted(x) for x in cutted]
    s1, s2 = [pd.DataFrame(pd.value_counts(x, sort=False)) for x in cutted]
    fig = plt.figure()
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)
    ax1 = s1.plot(kind='bar', ax=ax1, rot='45')
    ax2 = s2.plot(kind='bar', ax=ax2, rot='45')
    #-------------------------------------------------------------------------
    ticks = [ax1.get_xticks(), ax2.get_xticks()]
    ticks = [x[::thin] for x in ticks]  # Every other.
    #-------------------------------------------------------------------------
    ax1.set_xticks(ticks[0])
    ax2.set_xticks(ticks[1])
    return (ax1, ax2)


def get_mid(ind):
    ind = ind.strip('(]').split(', ')
    return np.mean([float(x) for x in ind])


def density_(df, n=100):
    x = pd.cut(df.t1, n)
    y = pd.cut(df.t2, n)
    x_counts = pd.value_counts(x)
    y_counts = pd.value_counts(y)
    x_mid = map(get_mid, x_counts.index)
    y_mid = map(get_mid, y_counts.index)
    lower = min(min(x_mid), min(y_mid))
    upper = max(max(x_mid), max(y_mid))
    arr = np.linspace(lower, upper, 100)
    grid = np.meshgrid(arr, arr)
    x_counts.index = x_mid
    y_counts.index = y_mid
    x_counts = x_counts.sort_index()
    y_counts = y_counts.sort_index()
#-----------------------------------------------------------------------------
# The fun
scatters = iter(scatter_(ctry) for ctry in declarants)
scatters_adj = iter(scatter_(ctry, inliers=True) for ctry in declarants)
mle = iter(mahalanobis_plot(ctry) for ctry in declarants)
mle_adj = iter(mahalanobis_plot(ctry, inliers=True) for ctry in declarants)
hists = iter(hist_(ctry=country) for country in declarants)
hists2 = iter(hist_2(ctry=country) for country in declarants)
outliers = iter(get_outliers(ctry=country) for country in declarants)
inliers = iter(get_inliers(ctry=country) for country in declarants)

zipped = izip(mle_adj, declarants)
for x, ctry in zipped:
    plt.savefig('/Users/tom/Desktop/outliers/outlier{}.png'.format(ctry),
                dpi=400, format='png')

for ctry in declarants:
    res = gmm_res.select('res_' + ctry)
    res = res.drop(get_outliers(res).index)
    mahalanobis_plot(ctry, df=res)
#-----------------------------------------------------------------------------
# Finding the outliers:

lens = {}
for country in declarants:
    df = get_outliers(ctry=country)
    lens[country] = len(df)
    gmm_res.append('round_1_{}'.format(country), df)
