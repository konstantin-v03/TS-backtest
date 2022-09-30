import pandas as pd
import numpy as np
import pandas_ta as pta
import ta


def calc(df: pd.DataFrame, initial_capital, percent, console_debug=False):
    capital = initial_capital

    curr_avg_price = 0.0
    curr_size = 0.0
    curr_side = ''
    curr_enter_count = 0

    tdf = pd.DataFrame(columns=['side', 'open', 'close', 'profit %', 'capital', 'enter_count'])

    for i in range(1, len(df)):
        if df.at[i - 1, 'side'] == 'long':
            if curr_side == 'short':
                capital += (1 + (curr_avg_price - df.at[i, 'open']) / curr_avg_price) * curr_avg_price * curr_size
                tdf.loc[len(tdf)] = ['short', curr_avg_price, df.at[i, 'open'],
                                     (curr_avg_price - df.at[i, 'open']) / curr_avg_price * 100,
                                     capital,
                                     curr_enter_count]
                curr_avg_price = 0
                curr_size = 0
                curr_enter_count = 0

            size = initial_capital * percent / 100 / df.at[i, 'open']
            capital -= initial_capital * percent / 100
            curr_avg_price = (curr_size * curr_avg_price + size * df.at[i, 'open']) / (curr_size + size)
            curr_size += size
            curr_enter_count += 1
            curr_side = 'long'
        elif df.at[i - 1, 'side'] == 'short':
            if curr_side == 'long':
                capital += (1 + (df.at[i, 'open'] - curr_avg_price) / curr_avg_price) * curr_avg_price * curr_size
                tdf.loc[len(tdf)] = ['long', curr_avg_price, df.at[i, 'open'],
                                     (df.at[i, 'open'] - curr_avg_price) / curr_avg_price * 100,
                                     capital,
                                     curr_enter_count]
                curr_avg_price = 0
                curr_size = 0
                curr_enter_count = 0

            size = initial_capital * percent / 100 / df.at[i, 'open']
            capital -= initial_capital * percent / 100
            curr_avg_price = (curr_size * curr_avg_price + size * df.at[i, 'open']) / (curr_size + size)
            curr_size += size
            curr_enter_count += 1
            curr_side = 'short'

        if console_debug:
            print(str(i) + '/' + str(len(df)) + ' is calculated!')

    return tdf


def points(df: pd.DataFrame, period, percent_change: float, pivot_bars, con_1_min_bars_back, trade_min_bars_back,
           rsi_filter=False,
           rsi_length=11,
           console_debug=False):
    df['percent'] = np.NaN
    df['short_condition_1'] = np.NaN
    df['short_condition_2'] = np.NaN
    df['long_condition_1'] = np.NaN
    df['long_condition_2'] = np.NaN
    df['rsi'] = pta.rsi(pd.Series(df.loc[:, 'close'].values), rsi_length) if rsi_filter else np.NaN
    df['side'] = np.NaN

    df = ta.fixnan(ta.pivot_low(df, pivot_bars), 'pivot_low')
    df = ta.fixnan(ta.pivot_high(df, pivot_bars), 'pivot_high')
    df = ta.lowest(df, period)
    df = ta.highest(df, period)

    for i in range(1, len(df)):
        df.at[i, 'percent'] = round(100 * (df.at[i, 'highest'] - df.at[i, 'lowest']) / df.at[i, 'lowest'], 1)

        if df.at[i, 'percent'] >= percent_change:
            df.at[i, 'short_condition_1'] = \
                df.at[i - 1, 'high'] == df.at[i - 1, 'highest'] and \
                df.at[i, 'high'] < df.at[i, 'highest'] and \
                ((df.at[i, 'highest'] - df.at[i, 'low']) * 3) < (df.at[i, 'low'] - df.at[i, 'lowest']) and \
                (rsi_filter is False or df.at[i, 'rsi'] >= 70)

            df.at[i, 'long_condition_1'] = \
                df.at[i - 1, 'low'] == df.at[i - 1, 'lowest'] and \
                df.at[i, 'low'] > df.at[i, 'lowest'] and \
                ((df.at[i, 'high'] - df.at[i, 'lowest']) * 3) < (df.at[i, 'highest'] - df.at[i, 'high']) and \
                (rsi_filter is False or df.at[i, 'rsi'] <= 30)
        else:
            df.at[i, 'short_condition_1'] = False
            df.at[i, 'long_condition_1'] = False

        df.at[i, 'short_condition_2'] = \
            df.at[i, 'pivot_high'] < df.at[i - 1, 'pivot_high'] and \
            ta.barsince(df, 'short_condition_1', i, True, max_barsince=con_1_min_bars_back) <= con_1_min_bars_back

        df.at[i, 'long_condition_2'] = \
            df.at[i, 'pivot_low'] > df.at[i - 1, 'pivot_low'] and \
            ta.barsince(df, 'long_condition_1', i, True, max_barsince=con_1_min_bars_back) <= con_1_min_bars_back

        if df.at[i, 'short_condition_2']:
            barsince = ta.barsince(df, 'short_condition_2', i, True, min_barsince=trade_min_bars_back)

            if np.isnan(barsince) or barsince > trade_min_bars_back:
                df.at[i, 'side'] = 'short'
        if df.at[i, 'long_condition_2']:
            barsince = ta.barsince(df, 'long_condition_2', i, True, min_barsince=trade_min_bars_back)

            if np.isnan(barsince) or barsince > trade_min_bars_back:
                df.at[i, 'side'] = 'long'

        if console_debug:
            print(str(i) + '/' + str(len(df)) + ' is processed!')

    return df
