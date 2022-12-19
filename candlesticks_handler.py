from binance.client import Client
import pandas as pd
from datetime import datetime
import calendar
import requests
import os

UNIX_TIME = 'Unix time'
OPEN_TIME = 'Open time'
OPEN = 'Open'
HIGH = 'High'
LOW = 'Low'
CLOSE = 'Close'
VOLUME = 'Volume'
CLOSE_TIME = 'Close time'
QUOTE_ASSET_VOLUME = 'Quote asset volume'
NUMBER_OF_TRADES = 'Number of trades'
TAKER_BUY_BASE_ASSET_VOLUME = 'Taker buy base asset volume'
TAKER_BUY_QUOTE_ASSET_VOLUME = 'Taker buy quote asset volume'
IGNORE = 'Ignore'

f_klines_dir = 'f_klines/'


def f_klines(symbol: str, interval: str, start_unix: int = None, end_unix: int = None, limit: int = None):
    url = 'https://fapi.binance.com/fapi/v1/klines'
    params = {'symbol': symbol, 'interval': interval, 'startTime': start_unix * 1000, 'endTime': end_unix * 1000,
              'limit': limit}

    r = requests.get(url, params)

    if r.status_code == 200:
        df = pd.DataFrame(r.json(),
                          columns=[OPEN_TIME,
                                   OPEN,
                                   HIGH,
                                   LOW,
                                   CLOSE,
                                   VOLUME,
                                   CLOSE_TIME,
                                   QUOTE_ASSET_VOLUME,
                                   NUMBER_OF_TRADES,
                                   TAKER_BUY_BASE_ASSET_VOLUME,
                                   TAKER_BUY_QUOTE_ASSET_VOLUME,
                                   IGNORE])

        df = df.drop(IGNORE, axis=1)
        df[UNIX_TIME] = df[OPEN_TIME] / 1000

        return f_klines_fix(df, unit='ms')
    else:
        print(r.json())


def f_klines_by_datetime(symbol: str, interval: str, start_datetime: datetime = None,
                         end_datetime: datetime = None):
    start_unix = calendar.timegm(start_datetime.utctimetuple())
    end_unix = calendar.timegm(end_datetime.utctimetuple())
    interval_s = interval_to_seconds(interval)

    if start_unix % interval_s != 0:
        start_unix = start_unix - start_unix % interval_s + interval_s

    if end_unix % interval_s != 0:
        end_unix = end_unix - end_unix % interval_s

    start_unix_save = start_unix
    end_unix_save = end_unix

    f_path = path(symbol, interval, start_unix, end_unix)

    if os.path.exists(f_path) and os.path.isfile(f_path):
        return f_klines_fix(pd.read_csv(f_path, index_col=0))

    unix_curr = calendar.timegm(datetime.utcnow().utctimetuple())
    end_unix = unix_curr if end_unix > unix_curr else end_unix

    limit = 1500

    df = pd.DataFrame()

    while start_unix + interval_s < end_unix:
        klines = f_klines(symbol, interval, start_unix,
                          start_unix + interval_s * limit - 1
                          if start_unix > interval_s * limit
                          else end_unix)
        if df.empty:
            df = klines
        else:
            df = pd.merge(df, klines, how='outer')

        start_unix = df.loc[len(df) - 1, UNIX_TIME] + interval_s

    if not os.path.exists(f_klines_dir):
        os.mkdir(f_klines_dir)

    df = df.loc[df[UNIX_TIME] <= end_unix]

    df.to_csv(path(symbol, interval, start_unix_save, end_unix_save))

    return df


def f_klines_fix(df, unit: str = None):
    df[UNIX_TIME] = df[UNIX_TIME].astype('int')
    df[OPEN_TIME] = pd.to_datetime(df[OPEN_TIME], unit=unit)
    df[OPEN] = df[OPEN].astype('float')
    df[HIGH] = df[HIGH].astype('float')
    df[LOW] = df[LOW].astype('float')
    df[CLOSE] = df[CLOSE].astype('float')
    df[VOLUME] = df[VOLUME].astype('float')

    df[CLOSE_TIME] = pd.to_datetime(df[CLOSE_TIME], unit=unit)
    df[QUOTE_ASSET_VOLUME] = df[QUOTE_ASSET_VOLUME].astype('float')
    df[NUMBER_OF_TRADES] = df[NUMBER_OF_TRADES].astype('int')
    df[TAKER_BUY_BASE_ASSET_VOLUME] = df[TAKER_BUY_BASE_ASSET_VOLUME].astype('float')
    df[TAKER_BUY_QUOTE_ASSET_VOLUME] = df[TAKER_BUY_QUOTE_ASSET_VOLUME].astype('float')

    return df


def path(symbol: str, interval: str, start_unix: int, end_unix: int):
    return f_klines_dir + \
           symbol + \
           '_' + \
           interval + \
           '_' + \
           str(start_unix) + \
           '_' + \
           str(end_unix) + \
           '.csv'


def interval_to_seconds(interval: str):
    if interval == Client.KLINE_INTERVAL_1MINUTE:
        return 60

    if interval == Client.KLINE_INTERVAL_5MINUTE:
        return 5 * 60

    if interval == Client.KLINE_INTERVAL_15MINUTE:
        return 15 * 60

    if interval == Client.KLINE_INTERVAL_1HOUR:
        return 60 * 60

    if interval == Client.KLINE_INTERVAL_1DAY:
        return 24 * 60 * 60
