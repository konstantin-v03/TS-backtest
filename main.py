import ts
import fapi
import time_se

df = fapi.klines_by_date('btcusdt', time_se.INTERVAL_5M, '20/09/22', '01/10/22')
df = ts.points(df, 72, 5.0, 3, 30, 10)
df.to_csv('out.csv')