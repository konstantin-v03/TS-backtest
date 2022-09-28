import pandas as pd
import numpy as np


def pivot_high(df: pd.DataFrame, n):
    df['pivot_high'] = np.NaN

    for i in range(n * 2, len(df) - 1):
        if df.at[i - n, 'high'] == df.loc[i - 2 * n:i + 1, 'high'].max():
            df.at[i, 'pivot_high'] = df.at[i - n, 'high']

    return df


def pivot_low(df: pd.DataFrame, n):
    df['pivot_low'] = np.NaN

    for i in range(n * 2, len(df) - 1):
        if df.at[i - n, 'low'] == df.loc[i - 2 * n:i + 1, 'low'].min():
            df.at[i, 'pivot_low'] = df.at[i - n, 'low']

    return df


def fixnan(df: pd.DataFrame, column: str):
    val = np.NaN

    for i in range(0, len(df)):
        if np.isnan(df.at[i, column]):
            df.at[i, column] = val
        else:
            val = df.at[i, column]

    return df


def highest(df: pd.DataFrame, p):
    df['highest'] = np.NaN

    for i in range(p - 1, len(df)):
        df.at[i, 'highest'] = df.loc[i - p + 1:i + 1, 'high'].max()

    return df


def lowest(df: pd.DataFrame, p):
    df['lowest'] = np.NaN

    for i in range(p - 1, len(df)):
        df.at[i, 'lowest'] = df.loc[i - p + 1:i + 1, 'low'].min()

    return df
