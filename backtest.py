from enum import Enum

import pandas as pd
import numpy as np

import ts


class Position(Enum):
    LONG = 'long'
    SHORT = 'short'


class DirFilter(Enum):
    LONGS = 'longs'
    SHORTS = 'shorts'
    ALL = 'all'


def calc(df: pd.DataFrame, capital, percent, pyramiding=1, dir_filter=DirFilter.ALL.value, console_debug=False):
    tdf = pd.DataFrame(columns=['date', 'position', 'open', 'close', 'size', 'PnL$', 'PnL%'])
    entry_count = 0

    for i in range(1, len(df)):
        action = df.at[i - 1, 'action']

        for j in reversed(range(len(tdf))):
            if tdf.at[j, 'position'] == Position.SHORT.value and \
                    np.isnan(tdf.at[j, 'close']) and \
                    (action == ts.Action.BUY_LONG.value or action == ts.Action.CLOSE_SHORT_STOP.value):
                tdf.at[j, 'close'] = df.at[i, 'open'] if action == ts.Action.BUY_LONG.value \
                    else df.at[i - 2, 'short_stop']
                tdf.at[j, 'PnL$'] = tdf.at[j, 'size'] * (tdf.at[j, 'open'] - tdf.at[j, 'close'])
                tdf.at[j, 'PnL%'] = -1 * 100 * (tdf.at[j, 'close'] - tdf.at[j, 'open']) / (tdf.at[j, 'open'])

                capital += tdf.at[j, 'size'] * tdf.at[j, 'open'] + tdf.at[j, 'PnL$']
                entry_count -= 1
            else:
                break

        for j in reversed(range(len(tdf))):
            if tdf.at[j, 'position'] == Position.LONG.value and \
                    np.isnan(tdf.at[j, 'close']) and \
                    (action == ts.Action.BUY_SHORT.value or action == ts.Action.CLOSE_LONG_STOP.value):
                tdf.at[j, 'close'] = df.at[i, 'open'] if action == ts.Action.BUY_SHORT.value \
                    else df.at[i - 2, 'long_stop']

                tdf.at[j, 'PnL$'] = tdf.at[j, 'size'] * (tdf.at[j, 'close'] - tdf.at[j, 'open'])
                tdf.at[j, 'PnL%'] = 100 * (tdf.at[j, 'close'] - tdf.at[j, 'open']) / (tdf.at[j, 'open'])

                capital += tdf.at[j, 'size'] * tdf.at[j, 'open'] + tdf.at[j, 'PnL$']
                entry_count -= 1
            else:
                break

        if entry_count < pyramiding:
            if (dir_filter == DirFilter.ALL.value or dir_filter == DirFilter.LONGS.value) and action == ts.Action.BUY_LONG.value:
                tdf.loc[len(tdf)] = [
                    df.at[i, 'date'],
                    Position.LONG.value,
                    df.at[i, 'open'],
                    np.NaN,
                    capital * percent / 100 / df.at[i, 'open'],
                    np.NaN,
                    np.NaN]

                capital *= (1 - percent / 100)
                entry_count += 1
            elif (dir_filter == DirFilter.ALL.value or dir_filter == DirFilter.SHORTS.value) and action == ts.Action.BUY_SHORT.value:
                tdf.loc[len(tdf)] = [
                    df.at[i, 'date'],
                    Position.SHORT.value,
                    df.at[i, 'open'],
                    np.NaN,
                    capital * percent / 100 / df.at[i, 'open'],
                    np.NaN,
                    np.NaN]

                capital *= (1 - percent / 100)
                entry_count += 1

        if console_debug:
            print(str(i) + '/' + str(len(df)) + ' is calculated!')

    return capital, tdf.round(1)
