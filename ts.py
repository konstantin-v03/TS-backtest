import pandas as pd
import numpy as np


def backtest(df: pd.DataFrame):
    side_index = list(df.columns).index('side')


def points(df: pd.DataFrame, period, perc_change: float, pivot_bars, condition_1_min_bars_back, trade_min_bars_back):
    df['l'] = np.NaN
    df['h'] = np.NaN
    df['perc'] = np.NaN
    df['pivot_low'] = np.NaN
    df['pivot_high'] = np.NaN
    df['short_condition_1'] = np.NaN
    df['short_condition_2'] = np.NaN
    df['long_condition_1'] = np.NaN
    df['long_condition_2'] = np.NaN
    df['side'] = np.NaN

    low_i = list(df.columns).index('low')
    high_i = list(df.columns).index('high')
    l_i = list(df.columns).index('l')
    h_i = list(df.columns).index('h')
    perc_i = list(df.columns).index('perc')
    pivot_l_i = list(df.columns).index('pivot_low')
    pivot_h_i = list(df.columns).index('pivot_high')
    s_condition_1_i = list(df.columns).index('short_condition_1')
    s_condition_2_i = list(df.columns).index('short_condition_2')
    l_condition_1_i = list(df.columns).index('long_condition_1')
    l_condition_2_i = list(df.columns).index('long_condition_2')
    side_i = list(df.columns).index('side')

    last_true_s_condition_1_i = 0
    last_true_s_condition_2_i = 0

    last_true_l_condition_1_i = 0
    last_true_l_condition_2_i = 0

    if len(df) > period:
        last_pivot = np.NaN

        for i in range(pivot_bars * 2, len(df) - 1):
            if df.iloc[i - pivot_bars, low_i] == df.iloc[i - 2 * pivot_bars:i + 1, low_i].min():
                last_pivot = df.iloc[i - pivot_bars, low_i]
            df.iloc[i, pivot_l_i] = last_pivot

        last_pivot = np.NaN

        for i in range(pivot_bars * 2, len(df) - 1):
            if df.iloc[i - pivot_bars, high_i] == df.iloc[i - 2 * pivot_bars:i + 1, high_i].max():
                last_pivot = df.iloc[i - pivot_bars, high_i]
            df.iloc[i, pivot_h_i] = last_pivot

        for i in range(period - 1, len(df)):
            li = i
            hi = i

            for hl in range(i - period + 1, i + 1):
                if df.iloc[li, low_i] > df.iloc[hl, low_i]:
                    li = hl
                if df.iloc[hi, high_i] < df.iloc[hl, high_i]:
                    hi = hl

            df.iloc[i, l_i] = df.iloc[li, low_i]
            df.iloc[i, h_i] = df.iloc[hi, high_i]
            df.iloc[i, perc_i] = round(100 * (df.iloc[hi, high_i] - df.iloc[li, low_i]) / df.iloc[
                li, low_i], 1)

            trig = df.iloc[i, perc_i] >= perc_change

            df.iloc[i, s_condition_1_i] = \
                trig and \
                df.iloc[i - 1, high_i] == df.iloc[i - 1, h_i] and \
                df.iloc[i, high_i] < df.iloc[i, h_i] and \
                ((df.iloc[i, h_i] - df.iloc[i, low_i]) * 3) < (df.iloc[i, low_i] - df.iloc[i, l_i])

            if df.iloc[i, s_condition_1_i]:
                last_true_s_condition_1_i = i

            df.iloc[i, s_condition_2_i] = \
                i - last_true_s_condition_1_i < condition_1_min_bars_back and \
                df.iloc[i, pivot_h_i] < df.iloc[i - 1, pivot_h_i]

            if df.iloc[i, s_condition_2_i]:
                if last_true_s_condition_2_i == np.NaN or i - last_true_s_condition_2_i > trade_min_bars_back:
                    df.iloc[i, side_i] = 'short'
                last_true_s_condition_2_i = i

            df.iloc[i, l_condition_1_i] = \
                trig and \
                df.iloc[i - 1, low_i] == df.iloc[i - 1, l_i] and \
                df.iloc[i, low_i] > df.iloc[i, l_i] and \
                ((df.iloc[i, high_i] - df.iloc[i, l_i]) * 3) < (df.iloc[i, h_i] - df.iloc[i, high_i])

            if df.iloc[i, l_condition_1_i]:
                last_true_l_condition_1_i = i

            df.iloc[i, l_condition_2_i] = \
                i - last_true_l_condition_1_i < condition_1_min_bars_back and \
                df.iloc[i, pivot_l_i] > df.iloc[i - 1, pivot_l_i]

            if df.iloc[i, l_condition_2_i]:
                if last_true_l_condition_2_i == np.NaN or i - last_true_l_condition_2_i > trade_min_bars_back:
                    df.iloc[i, side_i] = 'long'
                last_true_l_condition_2_i = i

    return df.drop(columns=['l', 'h', 'perc', 'pivot_high', 'pivot_low', 'short_condition_1', 'short_condition_2',
                            'long_condition_1', 'long_condition_2'], axis=1).dropna()
