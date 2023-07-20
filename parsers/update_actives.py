import json
import time
import requests
from datetime import datetime

from parsers.fonds import get_candles_tinkoff, TIMEFRAME_INTERVAL as TF_FONDS
from utils.indicators import ma_indicator, rsi_indicator, triangle_pattern, bollinger_lines, h_and_s, talib_indicators
from parsers.binance import get_candles_binance, TIMEFRAME_INTERVAL as TF_CRYPTO
from database import db_connect

TIMEFRAME_PERIODS = {
    '5m': 600,
    '30m': 1800,
    '1h': 3600,
    '4h': 14400,
    '1d': 86400,
    '1w': 604800,
    '1M': 604800
}


def write_actives(actives_list: list, type_actives: str, proxies=None, intervals=None):
    db = db_connect()
    if type_actives == 'fonds':
        get_candles_method = get_candles_tinkoff
        intervals = list(TF_FONDS.keys()) if not intervals else intervals
    else:
        get_candles_method = get_candles_binance
        intervals = list(TF_CRYPTO.keys()) if not intervals else intervals

    collection = db[type_actives]

    for active in actives_list:
        for interval in intervals:

            check_time_update = list(collection.find({'name': active, 'interval': interval}))
            if not check_time_update:
                pass
            elif int(datetime.now().timestamp()) - check_time_update[0]['time_update'] < TIMEFRAME_PERIODS[interval]:
                continue
            else:
                pass

            df_no_index = get_candles_method(active, interval, proxies)
            if df_no_index is None:
                break
            df_indexed = df_no_index.set_index('time')
            ma5, ma12, ma_points_red, ma_points_green = ma_indicator(df_indexed)
            rsi_plot, rsi_high70_plot, rsi_low30_plot, rsi_points_red, rsi_points_green = rsi_indicator(df_indexed)
            triangle_lines = triangle_pattern(df_no_index)
            upper_bollinger_line, lower_bollinger_line, bs_green, bs_red = bollinger_lines(df_indexed)
            vlines, sup_lines = h_and_s(df_no_index)
            talib_green, talib_red = talib_indicators(df_indexed)

            df_to_mongo = df_no_index
            df_to_mongo.index = df_to_mongo.index.astype('str')
            df_to_mongo['time'] = df_to_mongo['time'].astype('str')
            df_to_mongo = df_to_mongo.to_dict()

            indicators = {'ma': [list(ma5), list(ma12), list(ma_points_red), list(ma_points_green)],
                          'rsi': [list(rsi_plot), list(rsi_high70_plot), list(rsi_low30_plot), list(rsi_points_red), list(rsi_points_green)],
                          'triangle': triangle_lines,
                          'bollinger': [upper_bollinger_line.tolist(), lower_bollinger_line.tolist(), list(bs_red), list(bs_green)],
                          'has': [vlines, sup_lines],
                          'talib': [list(talib_green), list(talib_red)]
                          }
            data = {'plot_df': df_to_mongo,
                    'indicators': indicators,
                    'time_update': int(datetime.now().timestamp())}
            collection.find_one_and_update({'name': active, 'interval': interval}, {'$set': data}, upsert=True)
            time.sleep(1)
        time.sleep(1)


if __name__ == '__main__':
    #proxies = json.load(open('../proxies/proxies.json', 'r'))
    #write_actives(['BUSD'], 'crypto', proxies)
    base_endpoint = 'https://fapi.binance.com'
    path = '/fapi/v1/klines'
    params = {
        'symbol': "BUSD" + 'USDT',

    }

    response = requests.get(base_endpoint + 'api/v3/ticker/24hr', params=params)
    print(response)