from enum import Enum

import pandas as pd
import pandas_ta as pta
import numpy as np

import ta


class Action(Enum):
    BUY_LONG = "buy_long"
    CLOSE_LONG_STOP = "close_long_stop"
    BUY_SHORT = "buy_short"
    CLOSE_SHORT_STOP = "close_short_stop"


def points(df: pd.DataFrame,
           period,
           pivot_bars=3,
           atr_length=14,
           atr_mult=1.0,
           percent_trail=1,
           c1_min_bars_back=30,
           trade_min_bars_back=85,
           volatility_filter=True,
           volatility_df=None,
           volatility_length=14,
           rsi_filter=False,
           rsi_df=None,
           rsi_length=11,
           adx_filter=False,
           adx_df=None,
           adx_length=14,
           min_percent=5.0,
           console_debug=False):
    if volatility_filter:
        volatility_df = df if volatility_df is None else volatility_df

        df = df.merge(
            volatility_df.join(ta.volatility_index(volatility_df['close'], volatility_length)
                               .rename('volatility'))
            [['time', 'volatility']],
            how='left',
            on='time')

        df['volatility'] = ta.fixnan(df['volatility'])

    if rsi_filter:
        rsi_df = df if rsi_df is None else rsi_df

        df = df.merge(
            rsi_df.join(pta.rsi(rsi_df['close'], rsi_length)
                        .rename('rsi'))
            [['time', 'rsi']],
            how='left',
            on='time')

        df['rsi'] = ta.fixnan(df['rsi'])

    if adx_filter:
        adx_df = df if adx_df is None else adx_df

        df = df.merge(
            adx_df.join(pta.adx(adx_df['high'], adx_df['low'], adx_df['close'], length=adx_length))
            .rename(columns={'ADX_' + str(adx_length): 'adx',
                             'DMP_' + str(adx_length): 'di+',
                             'DMN_' + str(adx_length): 'di-'})
            [['time', 'di+', 'di-']],
            how='left',
            on='time')

        df['di+'] = ta.fixnan(df['di+'])
        df['di-'] = ta.fixnan(df['di-'])

    df['lowest'] = ta.lowest(df['low'], period)
    df['highest'] = ta.highest(df['high'], period)
    df['percent'] = np.NaN
    df['pivot_low'] = ta.fixnan(ta.pivotlow(df['low'], pivot_bars))
    df['pivot_high'] = ta.fixnan(ta.pivothigh(df['high'], pivot_bars))
    df['atr'] = pta.atr(df['high'], df['low'], df['close'], length=atr_length)
    df['sc1'] = False
    df['lc1'] = False
    df['sc2'] = False
    df['lc2'] = False
    df['action'] = np.NaN
    df['long_stop'] = np.NaN
    df['short_stop'] = np.NaN

    last_action = ""
    last_action_i = 0

    short_count = 1
    long_count = 1

    for i in range(1, len(df)):
        df.at[i, 'percent'] = round(100 * (df.at[i, 'highest'] - df.at[i, 'lowest']) / df.at[i, 'lowest'], 1)

        if df.at[i, 'percent'] > (df.at[i, 'volatility'] if volatility_filter else min_percent):
            df.at[i, 'sc1'] = \
                df.at[i - 1, 'high'] == df.at[i - 1, 'highest'] and \
                df.at[i, 'high'] < df.at[i, 'highest'] and \
                ((df.at[i, 'highest'] - df.at[i, 'low']) * 3) < (df.at[i, 'low'] - df.at[i, 'lowest']) and \
                (rsi_filter is False or df.at[i, 'rsi'] >= 70) and \
                (adx_filter is False or df.at[i, 'di+'] < df.at[i, 'di-'])

            df.at[i, 'lc1'] = \
                df.at[i - 1, 'low'] == df.at[i - 1, 'lowest'] and \
                df.at[i, 'low'] > df.at[i, 'lowest'] and \
                ((df.at[i, 'high'] - df.at[i, 'lowest']) * 3) < (df.at[i, 'highest'] - df.at[i, 'high']) and \
                (rsi_filter is False or df.at[i, 'rsi'] <= 30) and \
                (adx_filter is False or df.at[i, 'di+'] > df.at[i, 'di-'])

        df.at[i, 'sc2'] = \
            not np.isnan(ta.barsince(df['sc1'], i, True, max_barsince=c1_min_bars_back)) and \
            df.at[i, 'pivot_high'] < df.at[i - 1, 'pivot_high']

        df.at[i, 'lc2'] = \
            not np.isnan(ta.barsince(df['lc1'], i, True, max_barsince=c1_min_bars_back)) and \
            df.at[i, 'pivot_low'] > df.at[i - 1, 'pivot_low']

        if last_action == Action.BUY_SHORT.value and df.at[i, 'high'] > df.at[i - 1, 'short_stop']:
            df.at[i, 'action'] = Action.CLOSE_SHORT_STOP.value
            last_action = Action.CLOSE_SHORT_STOP.value
            last_action_i = i

        if last_action == Action.BUY_LONG.value and df.at[i, 'low'] < df.at[i - 1, 'long_stop']:
            df.at[i, 'action'] = Action.CLOSE_LONG_STOP.value
            last_action = Action.CLOSE_LONG_STOP.value
            last_action_i = i

        if last_action == Action.BUY_SHORT.value:
            if df.at[i, 'close'] < df.at[last_action_i + 1, 'open'] * (1 - (percent_trail * short_count) / 100):
                df.at[i, 'short_stop'] = df.at[last_action_i + 1, 'open'] * (1 - (percent_trail * (short_count - 1)) / 100)
                short_count += 1
            elif short_count == 1:
                df.at[i, 'short_stop'] = df.at[i, 'highest'] + atr_mult * df.at[i, 'atr']
            else:
                df.at[i, 'short_stop'] = df.at[i - 1, 'short_stop']
        else:
            short_count = 1

        if last_action == Action.BUY_LONG.value:
            if df.at[i, 'close'] > df.at[last_action_i + 1, 'open'] * (1 + (percent_trail * long_count) / 100):
                df.at[i, 'long_stop'] = df.at[last_action_i + 1, 'open'] * (1 + (percent_trail * (long_count - 1)) / 100)
                long_count += 1
            elif long_count == 1:
                df.at[i, 'long_stop'] = df.at[i, 'lowest'] - atr_mult * df.at[i, 'atr']
            else:
                df.at[i, 'long_stop'] = df.at[i - 1, 'long_stop']
        else:
            long_count = 1

        if df.at[i, 'sc2'] and np.isnan(ta.barsince(df['sc2'], i - 1, True, max_barsince=trade_min_bars_back)):
            df.at[i, 'action'] = Action.BUY_SHORT.value
            last_action = Action.BUY_SHORT.value
            last_action_i = i

        if df.at[i, 'lc2'] and np.isnan(ta.barsince(df['lc2'], i - 1, True, max_barsince=trade_min_bars_back)):
            df.at[i, 'action'] = Action.BUY_LONG.value
            last_action = Action.BUY_LONG.value
            last_action_i = i

        if console_debug:
            print(str(i) + '/' + str(len(df)) + ' is processed!')

    return df
