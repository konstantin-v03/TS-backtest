import time_se
import fapi
import ts

dir_name = 'csv/'

df = fapi.klines_by_date('btcusdt', time_se.INTERVAL_15M, '1/10/22', '1/12/22', console_debug=True)

df.to_csv(dir_name + 'btcusdtperp-15m.csv')

df = ts.points(df, 96, console_debug=True)

df.to_csv(dir_name + 'backtest-btcusdtperp-15m.csv')
