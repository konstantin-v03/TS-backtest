import pandas as pd

import backtest
import time_se
import fapi
import ts

dir_name = 'csv/'

df = fapi.klines_by_date('btcusdt', time_se.INTERVAL_15M, '08/09/19', '12/10/22')
df1d = fapi.klines_by_date('btcusdt', time_se.INTERVAL_1D, '08/09/19', '12/10/22')

# df = fapi.klines_by_date('btcusdt', time_se.INTERVAL_15M, '01/06/22', '12/10/22')
# df1d = fapi.klines_by_date('btcusdt', time_se.INTERVAL_1D, '01/05/22', '12/10/22')

df.to_csv(dir_name + 'btcusdtperp-15m.csv')
df1d.to_csv(dir_name + 'btcusdtperp-1d.csv')

# df = pd.read_csv(dir_name + 'btcusdtperp-15m.csv', index_col=0)
# df1d = pd.read_csv(dir_name + 'btcusdtperp-1d.csv', index_col=0)

df = ts.points(df, 96, volatility_filter=True, volatility_df=df1d)

df.to_csv(dir_name + 'backtest-btcusdtperp-15m.csv')

# df = pd.read_csv(dir_name + 'backtest-btcusdtperp-15m.csv', index_col=0)

initial_capital = 1_000_000

capital, df = backtest.calc(df, initial_capital, 100)
print((1 - initial_capital / capital) * 100)

df.to_csv(dir_name + 'trades-shorts-btcusdtperp-15m.csv')