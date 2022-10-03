from enum import Enum

import pandas as pd
import numpy as np

import ts


class Position(Enum):
    LONG = 'long'
    SHORT = 'short'


def calc(df: pd.DataFrame, capital, percent, console_debug=False):
    tdf = pd.DataFrame(columns=['date', 'position', 'open', 'close', 'size', 'PnL$', 'PnL%'])

    for i in range(1, len(df)):
        action = df.at[i - 1, 'action']

        if action == ts.Action.BUY_LONG.value or action == ts.Action.CLOSE_SHORT.value:
            for j in reversed(range(len(tdf))):
                if np.isnan(tdf.at[j, 'close']) is False or tdf.at[j, 'position'] != Position.SHORT.value:
                    break

                tdf.at[j, 'close'] = df.at[i, 'open']
                tdf.at[j, 'PnL$'] = tdf.at[j, 'size'] * (tdf.at[j, 'open'] - tdf.at[j, 'close'])
                tdf.at[j, 'PnL%'] = -1 * 100 * (tdf.at[j, 'close'] - tdf.at[j, 'open']) / (tdf.at[j, 'open'])

                capital += tdf.at[j, 'size'] * tdf.at[j, 'open'] + tdf.at[j, 'PnL$']

        if action == ts.Action.BUY_SHORT.value or action == ts.Action.CLOSE_LONG.value:
            for j in reversed(range(len(tdf))):
                if np.isnan(tdf.at[j, 'close']) is False or tdf.at[j, 'position'] != Position.LONG.value:
                    break

                tdf.at[j, 'close'] = df.at[i, 'open']
                tdf.at[j, 'PnL$'] = tdf.at[j, 'size'] * (tdf.at[j, 'close'] - tdf.at[j, 'open'])
                tdf.at[j, 'PnL%'] = 100 * (tdf.at[j, 'close'] - tdf.at[j, 'open']) / (tdf.at[j, 'open'])

                capital += tdf.at[j, 'size'] * tdf.at[j, 'open'] + tdf.at[j, 'PnL$']

        if action == ts.Action.BUY_LONG.value:
            tdf.loc[len(tdf)] = [
                df.at[i, 'date'],
                Position.LONG.value,
                df.at[i, 'open'],
                np.NaN,
                capital * percent / 100 / df.at[i, 'open'],
                np.NaN,
                np.NaN]

            capital *= (1 - percent / 100)
        elif action == ts.Action.BUY_SHORT.value:
            tdf.loc[len(tdf)] = [
                df.at[i, 'date'],
                Position.SHORT.value,
                df.at[i, 'open'],
                np.NaN,
                capital * percent / 100 / df.at[i, 'open'],
                np.NaN,
                np.NaN]

            capital *= (1 - percent / 100)

        if console_debug:
            print(str(i) + '/' + str(len(df)) + ' is calculated!')

    return capital, tdf.dropna().round(1)
