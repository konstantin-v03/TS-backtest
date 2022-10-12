import pandas as pd
from pandas import Series
import pandas_ta as pta
import numpy as np
import math


def pivothigh(series: Series, n):
    res = pd.Series(np.NaN, index=series.index)

    for i in range(n * 2, len(series) - 1):
        if series[i - n] == series[i - 2 * n:i + 1].max():
            res[i] = series.at[i - n]

    return res


def pivotlow(series: Series, n):
    res = pd.Series(np.NaN, index=series.index)

    for i in range(n * 2, len(series) - 1):
        if series[i - n] == series[i - 2 * n:i + 1].min():
            res[i] = series[i - n]

    return res


def fixnan(series: Series):
    res = series.copy()
    value = np.NaN

    for i in range(0, len(series)):
        if np.isnan(series[i]):
            res[i] = value
        else:
            value = series[i]

    return res


def highest(series: Series, p):
    res = pd.Series(np.NaN, index=series.index)

    for i in range(p - 1, len(series)):
        res[i] = series[i - p + 1:i + 1].max()

    return res


def lowest(series: Series, p):
    res = pd.Series(np.NaN, index=series.index)

    for i in range(p - 1, len(series)):
        res[i] = series[i - p + 1:i + 1].min()

    return res


def barsince(series: Series, index, value, max_barsince=np.NaN, min_barsince=np.NaN):
    max_index = 0 if np.isnan(max_barsince) or index - max_barsince < 0 else index - max_barsince
    min_index = index if np.isnan(min_barsince) else index - min_barsince

    for i in reversed(range(max_index, min_index + 1)):
        if series[i] == value:
            return index - i

    return np.NaN


def volatility_index(series: Series, length):
    log = pd.Series(np.NaN, index=series.index)

    for i in range(1, len(series)):
        log[i] = math.log(series[i] / series[i - 1])

    return 100 * pta.stdev(log, length, ddof=0)
