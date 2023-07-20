import pprint

from itertools import groupby
from datetime import datetime
from database import db_connect

db = db_connect()

AMOUNT_CANDLES_CHECK = {
    '5m': 2,
    '30m': 3,
    '1h': 3,
    '4h': 3,
    '1d': 3,
    '1w': 2,
    '1M': 2
}

TIME_DURATION_CHECK = {
    '5m': 600,
    '30m': 1800,
    '1h': 3600,
    '4h': 14400,
    '1d': 86400,
    '1w': 604800,
    '1M': 604800
}


def find_triangle(type_active, indicator):
    actives = list(db[type_active].find({}, {'_id': 0}))
    triangles = []
    cur_time = datetime.now().timestamp()
    for active in actives:
        if active['indicators']['triangle']:
            first_end_time = active['indicators']['triangle'][-1][-1][0]
            if cur_time - int(first_end_time.timestamp()) < TIME_DURATION_CHECK[active['interval']]:
                triangles.append(
                    {
                        'active': active['name'],
                        'interval': active['interval'],
                        'indicator': indicator
                    }
                )
    return triangles


def find_signals(type_active, indicator, number_list):
    actives = list(db[type_active].find({}, {'_id': 0}))
    green = []
    multiplier = 1
    if indicator == 'rsi':
        multiplier = 3
    for active in actives:
        checked_list = active['indicators'][indicator][number_list][
                       -AMOUNT_CANDLES_CHECK[active['interval']] * multiplier:]
        for item in checked_list:
            str_item = str(item)
            if str_item != 'nan':
                green.append(
                    {
                        'active': active['name'],
                        'interval': active['interval'],
                        'indicator': indicator
                    }
                )
                break
    return green


def update_signals(type_active):
    ma = find_signals(type_active, 'ma', 3)
    rsi = find_signals(type_active, 'rsi', 4)
    bb = find_signals(type_active, 'bollinger', 3)
    talib = find_signals(type_active, 'talib', 0)
    triangle = find_triangle(type_active, 'triangle')
    result = ma + rsi + bb + talib + triangle

    group_conf = lambda x: (x.get("active"), x.get("interval"))
    group_res = [
        dict(
            active=a[0],
            interval=a[1],
            indicator=[x.get("indicator") for x in b])
        for a, b in groupby(sorted(result, key=group_conf), key=group_conf)
    ]

    res_temp = []
    for i in group_res:
        if len(i['indicator']) > 1:
            res_temp.append(i)

    result_final = sorted(res_temp, key=lambda d: len(d['indicator']), reverse=True)

    data = {
        'signals': result_final
    }
    db['signals'].find_one_and_update({'type_active': type_active, 'access': 'all'}, {'$set': data}, upsert=True)

    public_actives = list(db[f'patterns_app_{type_active}array'].find({}, {'_id': 0}))
    actives_public_list = [active['name'] for active in public_actives]

    result_public_list = [signal for signal in result_final if signal['active'] in actives_public_list]

    data = {
        'signals': result_public_list
    }
    db['signals'].find_one_and_update({'type_active': type_active, 'access': 'public'}, {'$set': data}, upsert=True)


if __name__ == '__main__':
    # update('crypto')
    update_signals('fonds')
