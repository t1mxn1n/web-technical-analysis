import datetime

import requests
import json
from loguru import logger
from database import db_connect

base_url = 'https://api.binance.com/'


def update():
    db = db_connect()
    response_symbols = requests.get(base_url + 'api/v3/exchangeInfo')
    response_symbols_json = response_symbols.json()
    symbols = []
    for symbol in response_symbols_json['symbols']:
        if symbol["quoteAsset"] == 'USDT':
            symbols.append(symbol['baseAsset'])
    if symbols:
        db['crypto_symbols'].drop()

    unique_symbols = list(set(symbols))

    logger.info(f'Всего {len(unique_symbols)} токенов')
    time_start = datetime.datetime.now()

    proxies = json.load(open('../proxies/proxies.json', 'r'))
    for symbol in unique_symbols:
        param = {'symbol': symbol + 'USDT'}
        for proxy in proxies:
            proxies_settings = {'http': proxy}
            temp = proxies.pop(0)
            proxies.append(temp)
            response = requests.get(base_url + 'api/v3/ticker/24hr', params=param, proxies=proxies_settings)
            if response.status_code == 200:
                response_json = response.json()
                db['crypto_symbols'].find_one_and_update(
                    {'symbol': symbol},
                    {'$set': {'volume_usdt': float(response_json['quoteVolume']),
                              'price_change': float(response_json['priceChangePercent'])}},
                    upsert=True)
                break
            else:
                print(symbol)
                print(response.status_code)
    logger.info(f'Обновление закончилось за {datetime.datetime.now() - time_start}')


if __name__ == '__main__':
    update()
