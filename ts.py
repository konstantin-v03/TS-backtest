import pandas as pd
import numpy as np
import ta


def points(df: pd.DataFrame, period, perc_change: float, pivot_bars, condition_1_min_bars_back, trade_min_bars_back):
    df['percent'] = np.NaN
    df['short_condition_1'] = np.NaN
    df['short_condition_2'] = np.NaN
    df['long_condition_1'] = np.NaN
    df['long_condition_2'] = np.NaN
    df['side'] = np.NaN

    df = ta.fixnan(ta.pivot_low(df, pivot_bars), 'pivot_low')
    df = ta.fixnan(ta.pivot_high(df, pivot_bars), 'pivot_high')
    df = ta.lowest(df, period)
    df = ta.highest(df, period)

    last_true_s_condition_1_i = 0
    last_true_s_condition_2_i = 0

    last_true_l_condition_1_i = 0
    last_true_l_condition_2_i = 0

    for i in range(period - 1, len(df)):
        df.at[i, 'percent'] = round(100 * (df.at[i, 'highest'] - df.at[i, 'lowest']) / df.at[i, 'lowest'], 1)

        trig = df.at[i, 'percent'] >= perc_change

        df.at[i, 'short_condition_1'] = \
            trig and \
            df.at[i - 1, 'high'] == df.at[i - 1, 'highest'] and \
            df.at[i, 'high'] < df.at[i, 'highest'] and \
            ((df.at[i, 'highest'] - df.at[i, 'low']) * 3) < (df.at[i, 'low'] - df.at[i, 'lowest'])

        if df.at[i, 'short_condition_1']:
            last_true_s_condition_1_i = i

        df.at[i, 'short_condition_2'] = \
            i - last_true_s_condition_1_i < condition_1_min_bars_back and \
            df.at[i, 'pivot_high'] < df.at[i - 1, 'pivot_high']

        if df.at[i, 'short_condition_2']:
            if last_true_s_condition_2_i == np.NaN or i - last_true_s_condition_2_i > trade_min_bars_back:
                df.at[i, 'side'] = 'short'
            last_true_s_condition_2_i = i

        df.at[i, 'long_condition_1'] = \
            trig and \
            df.at[i - 1, 'low'] == df.at[i - 1, 'lowest'] and \
            df.at[i, 'low'] > df.at[i, 'lowest'] and \
            ((df.at[i, 'high'] - df.at[i, 'lowest']) * 3) < (df.at[i, 'highest'] - df.at[i, 'high'])

        if df.at[i, 'long_condition_1']:
            last_true_l_condition_1_i = i

        df.at[i, 'long_condition_2'] = \
            i - last_true_l_condition_1_i < condition_1_min_bars_back and \
            df.at[i, 'pivot_low'] > df.at[i - 1, 'pivot_low']

        if df.at[i, 'long_condition_2']:
            if last_true_l_condition_2_i == np.NaN or i - last_true_l_condition_2_i > trade_min_bars_back:
                df.at[i, 'side'] = 'long'
            last_true_l_condition_2_i = i

    return df.drop(columns=['lowest', 'highest', 'percent', 'pivot_high', 'pivot_low', 'short_condition_1', 'short_condition_2',
                            'long_condition_1', 'long_condition_2'], axis=1).dropna()
