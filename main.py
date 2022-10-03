import backtest
import time_se
import fapi
import ts


df = fapi.klines_by_date('btcusdt', time_se.INTERVAL_15M, '08/09/19', '02/10/22', console_debug=True)
df.to_csv('csv/btcusdt-15m-btcusdtperp.csv')

df = ts.points(df, 96, 7.0, 3, 30, console_debug=True)

df.to_csv('csv/ts-btcusdt-15m-btcusdtperp.csv')

capital, df = backtest.calc(df, 1_000_000, 10, console_debug=True)

df.to_csv('csv/backtest-btcusdt-15m-btcusdtperp.csv')
print(capital)
