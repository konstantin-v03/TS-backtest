from enum import Enum

import pandas as pd
import pandas_ta as pta
import numpy as np

import ta


class Action(Enum):
    BUY_LONG = "buy long"
    CLOSE_LONG = "close long"
    BUY_SHORT = "buy short"
    CLOSE_SHORT = "close short"


def points(df: pd.DataFrame, period, percent_change: float, pivot_bars, con_1_min_bars_back,
           rsi_filter=False,
           rsi_length=11,
           adx_filter=False,
           adx_df=None,
           adx_length=14,
           console_debug=False):
    df['percent'] = np.NaN
    df['red_line'] = False
    df['green_line'] = False
    df['rsi'] = pta.rsi(df.loc[:, 'close'], rsi_length) if rsi_filter else np.NaN

    if adx_filter:
        adx_df = df if adx_df is None else adx_df

        df = df.merge(
            adx_df.join(pta.adx(adx_df.loc[:, 'high'], adx_df.loc[:, 'low'], adx_df.loc[:, 'close'], length=adx_length))
            .rename(columns={'ADX_' + str(adx_length): 'adx',
                             'DMP_' + str(adx_length): 'di+',
                             'DMN_' + str(adx_length): 'di-'})
            [['time', 'di+', 'di-']],
            how='left',
            on='time')

        df = ta.fixnan(df, 'di+')
        df = ta.fixnan(df, 'di-')

    df = ta.fixnan(ta.pivot_low(df, pivot_bars), 'pivot_low')
    df = ta.fixnan(ta.pivot_high(df, pivot_bars), 'pivot_high')
    df = ta.lowest(df, period)
    df = ta.highest(df, period)

    df['action'] = np.NaN

    for i in range(1, len(df)):
        df.at[i, 'percent'] = round(100 * (df.at[i, 'highest'] - df.at[i, 'lowest']) / df.at[i, 'lowest'], 1)

        if df.at[i, 'percent'] >= percent_change:
            df.at[i, 'red_line'] = \
                df.at[i - 1, 'high'] == df.at[i - 1, 'highest'] and \
                df.at[i, 'high'] < df.at[i, 'highest'] and \
                ((df.at[i, 'highest'] - df.at[i, 'low']) * 3) < (df.at[i, 'low'] - df.at[i, 'lowest']) and \
                (rsi_filter is False or df.at[i, 'rsi'] >= 70) and \
                (adx_filter is False or df.at[i, 'di+'] < df.at[i, 'di-'])

            df.at[i, 'green_line'] = \
                df.at[i - 1, 'low'] == df.at[i - 1, 'lowest'] and \
                df.at[i, 'low'] > df.at[i, 'lowest'] and \
                ((df.at[i, 'high'] - df.at[i, 'lowest']) * 3) < (df.at[i, 'highest'] - df.at[i, 'high']) and \
                (rsi_filter is False or df.at[i, 'rsi'] <= 30) and \
                (adx_filter is False or df.at[i, 'di+'] > df.at[i, 'di-'])

        bs_red_line = ta.barsince(df, 'red_line', i, True, max_barsince=con_1_min_bars_back)
        bs_short = ta.barsince(df, 'action', i, Action.BUY_SHORT.value, max_barsince=bs_red_line + 1)

        bs_green_line = ta.barsince(df, 'green_line', i, True, max_barsince=con_1_min_bars_back)
        bs_long = ta.barsince(df, 'action', i, Action.BUY_LONG.value, max_barsince=bs_green_line + 1)

        df.at[i, 'action'] = \
            Action.BUY_SHORT.value if \
            df.at[i, 'pivot_high'] < df.at[i - 1, 'pivot_high'] and \
            bs_red_line <= con_1_min_bars_back and \
            np.isnan(bs_short) else \
            Action.BUY_LONG.value if \
            df.at[i, 'pivot_low'] > df.at[i - 1, 'pivot_low'] and \
            bs_green_line <= con_1_min_bars_back and \
            np.isnan(bs_long) else np.NaN

        if console_debug:
            print(str(i) + '/' + str(len(df)) + ' is processed!')

    return df[['time', 'date', 'open', 'high', 'low', 'close', 'action']]
