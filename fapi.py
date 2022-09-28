import requests
import pandas as pd
import datetime
import calendar
from datetime import datetime
import time_se
import constant


FAPI_KLINES_MAX_LIMIT = 1500


def klines(symbol, timeframe, start_time=None, end_time=None, limit=None):
    url = 'https://fapi.binance.com/fapi/v1/klines'
    params = {'symbol': symbol, 'interval': timeframe, 'startTime': start_time, 'endTime': end_time, 'limit': limit}
    r = requests.get(url, params)

    if r.status_code == 200:
        df = pd.DataFrame(r.json())
        m = pd.DataFrame()

        m['time'] = df.iloc[:, 0].astype(int)
        m['date'] = pd.to_datetime(m['time'], unit='ms').astype(str)
        m['open'] = df.iloc[:, 1].astype(float)
        m['high'] = df.iloc[:, 2].astype(float)
        m['low'] = df.iloc[:, 3].astype(float)
        m['close'] = df.iloc[:, 4].astype(float)

        return m
    return ''


def klines_by_date(symbol, timeframe, start_date, end_date, console_debug=False):
    unix_start = time_se.unix_to_ms(calendar.timegm(datetime.strptime(start_date, constant.TIME_FORMAT).timetuple()))
    unix_end = time_se.unix_to_ms(calendar.timegm(datetime.strptime(end_date, constant.TIME_FORMAT).timetuple()))
    unix_curr = time_se.unix_to_ms(calendar.timegm(datetime.utcnow().utctimetuple()))

    unix_end = unix_curr if unix_end > unix_curr else unix_end

    df = pd.DataFrame(columns=['time', 'date', 'open', 'high', 'low', 'close'])

    total_klines = int((unix_end - unix_start) / time_se.tf_to_ms(timeframe))

    while unix_start < unix_end:
        df = pd.merge(df, klines(symbol, timeframe, unix_start,
                                 unix_start + time_se.tf_to_ms(timeframe) * FAPI_KLINES_MAX_LIMIT - 1
                                 if unix_start > time_se.tf_to_ms(timeframe) * FAPI_KLINES_MAX_LIMIT
                                 else unix_end), how='outer')

        if console_debug:
            print(str(len(df)) + '/' + str(total_klines) + ' is received!')

        unix_start = df.iloc[len(df) - 1, 0] + time_se.tf_to_ms(timeframe)
    return df