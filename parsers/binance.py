import pandas as pd
import requests
from datetime import datetime
from pandas import DataFrame, to_datetime
from pprint import pprint
from decouple import config
from loguru import logger

from database import db_connect
db = db_connect()

TIMEFRAME_INTERVAL = {
    '5m': 86400,     # 1 day 288
    '30m': 432000,   # 5 day 240
    '1h': 691200,   # 9 day 288
    '4h': 2592000,   # 1 month 180
    '1d': 18144000,  # 7 month 210
    '1w': 62208000,  # 2 years 103
    '1M': 0          # all 45
}

"""
[
  [
    1499040000000,      // Open time
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume
    1499644799999,      // Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "17928899.62484339" // Ignore.
  ]
]
"""


def get_candles_binance(symbol, timeframe, proxies):

    logger.info(f'collecting {symbol}_{timeframe}')
    base_endpoint = 'https://fapi.binance.com'
    path = '/fapi/v1/klines'
    params = {
        'symbol': symbol + 'USDT',
        'interval': timeframe,
        'limit': 1500,
    }
    if timeframe != '1M':
        params['startTime'] = (int(datetime.now().timestamp()) - TIMEFRAME_INTERVAL[timeframe]) * 1000

    error_counts = 0
    if proxies is None:
        response = requests.get(base_endpoint + path, params=params)
        if response.status_code == 200:
            response_json = response.json()
    else:
        for proxy in proxies:
            proxies_settings = {'http': proxy}
            response = requests.get(base_endpoint + path, params=params, proxies=proxies_settings)
            temp = proxies.pop(0)
            proxies.append(temp)

            if response.status_code == 200:
                response_json = response.json()
                break
            else:
                error_counts += 1
                logger.error(f'status code: {response.status_code}')

            if error_counts == 4:
                db['patterns_app_cryptoarray'].delete_one({'name': symbol})
                logger.error(f'deleted symbol: {symbol}')
                return None

    df_candles = DataFrame(response_json)
    fields = ['time', 'open', 'high', 'low', 'close', 'volume']
    columns_names = {index: value for index, value in enumerate(fields)}

    df_candles.rename(columns=columns_names, inplace=True)

    df_candles.drop([6, 7, 8, 9, 10, 11], axis='columns', inplace=True)
    df_candles[fields] = df_candles[fields].astype(float)
    df_candles['time'] = to_datetime(df_candles['time'], unit='ms')

    # df_indexed = df_candles.set_index('time')

    return df_candles


if __name__ == '__main__':
    active = 'btc'
    tf = '4h'
    # https://fapi.binance.com/fapi/v1/klines?symbol=pepeUSDT&interval=1h&limit=500

    a = get_candles_binance(active, tf, None)
    print(a)
    #print(df_index.to_records(index=True))
    #import pymongo
    #client = pymongo.MongoClient('mongodb://localhost:27017/')
    # print(df_no_index)
    # db = client['patterns']
    # crypto = db['crypto']
    #
    # df_no_index = crypto.find_one({'name': active})
    # df_no_index = pd.DataFrame(df_no_index['plot_df'])
    # df_no_index['time'] = to_datetime(df_no_index['time'])
    # df_no_index.index = df_no_index.index.astype('int64')
    # print(df_no_index)
    # df_index = df_no_index.set_index('time')


    # from fonds import make_plot
    #make_plot(active, tf, df_index, df_no_index)

