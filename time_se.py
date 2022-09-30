INTERVAL_5M = '5m'
INTERVAL_15M = '15m'
INTERVAL_1H = '1h'
INTERVAL_4H = '4h'
INTERVAL_1D = '1d'


def tf_to_ms(interval):
    if interval == INTERVAL_5M:
        return 5 * 60 * 1000
    elif interval == INTERVAL_15M:
        return 15 * 60 * 1000
    elif interval == INTERVAL_1H:
        return 60 * 60 * 1000
    elif interval == INTERVAL_4H:
        return 4 * 60 * 60 * 1000
    elif interval == INTERVAL_1D:
        return 24 * 60 * 60 * 1000


def unix_to_ms(unix):
    return int(unix * 1000)
