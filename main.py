import ts
import fapi
import time_se

df = fapi.klines_by_date('btcusdt', time_se.INTERVAL_5M, '08/09/19', '01/10/22', console_debug=True)
df.to_csv('btcusdtperp-5m-08-09-19-01-10-22.csv')

df = ts.points(df, 72, 5.0, 3, 30, 30, rsi_filter=True, console_debug=True)

df.to_csv('points-temp-btcusdtperp-5m-08-09-19-01-10-22.csv')

df = ts.calc(df, 10000, 20, console_debug=True)

print('Capital:', df.loc[len(df) - 1, 'capital'])
print('Mean enter count:', df.loc[:, 'enter_count'].mean())
print('Max enter count:', df.loc[:, 'enter_count'].max())

df.to_csv('points-btcusdtperp-5m-08-09-19-01-10-22.csv')
