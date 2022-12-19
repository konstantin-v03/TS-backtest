from binance import Client
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
import ta
import candlesticks_handler as ch
import ts


def prophet(symbol: str, interval: str, bars: int, periods: int, total: int, freq: str, df: pd.DataFrame):
    if total < bars:
        total = bars

    end_datetime = datetime.datetime.utcnow()
    start_datetime = end_datetime - datetime.timedelta(seconds=ch.interval_to_seconds(interval) * total)

    klines_orig = ch.f_klines_by_datetime(symbol, interval, start_datetime, end_datetime)
    klines = klines_orig[[ch.UNIX_TIME, ch.OPEN, ch.HIGH, ch.LOW, ch.CLOSE]]
    unix_series = klines[ch.UNIX_TIME]

    klines = klines[[ch.UNIX_TIME, ch.OPEN, ch.HIGH, ch.LOW, ch.CLOSE]]
    klines[ch.UNIX_TIME] = pd.to_datetime(klines[ch.UNIX_TIME], unit='s').apply(mpl_dates.date2num)

    fig, ax = plt.subplots(figsize=(16, 12))
    candlestick_ohlc(ax, klines.values, width=0.01, colorup='green', colordown='red', alpha=0.8)
    date_format = mpl_dates.DateFormatter('%m-%d-%h')
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()
    fig.tight_layout()

    for index, row in df.iterrows():
        trade_datetime = datetime.datetime.utcfromtimestamp(row['time'] / 1000)

        if trade_datetime > start_datetime:
            color = 'green' if row['action'] == ts.Action.BUY_LONG.value else 'red'
            plt.axvline(trade_datetime, color=color)

    df['time'] = df['time'] / 1000
    time_list = df['time'].tolist()

    for i in range(bars, total):
        if unix_series[i] in time_list:
            klines_split = klines_orig.iloc[i - bars:i]

            klines_split.reset_index(inplace=True)

            forecast = ta.predict(klines_split[ch.OPEN_TIME],
                                (klines_split[ch.OPEN] +
                                klines_split[ch.CLOSE] +
                                klines_split[ch.HIGH] +
                                klines_split[ch.LOW]) / 4,
                                periods,
                                freq=freq)

            plt.plot(forecast['ds'].tail(periods + 1), forecast['yhat'].tail(periods + 1), color='black', linewidth=2)

    plt.show()


df = pd.read_csv('csv/backtest-btcusdtperp-15m.csv', index_col=0)

df = df[df['action'].notna()]

df = df[df['action'].str.contains(str(ts.Action.BUY_LONG.value) + "|" + str(ts.Action.BUY_SHORT.value))]
df.reset_index(inplace=True)
df = df[['time', 'action']]

prophet("btcusdt", Client.KLINE_INTERVAL_15MINUTE, 1000, 96, 5000, '15min', df)
