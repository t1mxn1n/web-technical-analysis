import pprint
from itertools import groupby
from datetime import datetime

from database import db_connect

db = db_connect()

TIMES_DELTA = {
    '5m': 1800,
    '30m': 1800 * 2,
    '1h': 3600 * 2,
    '4h': 14400 * 2,
    '1d': 86400 * 2,
    '1w': 604800 * 2,
    '1M': 604800 * 2
}


def write_notification(type_active):
    users = list(db['users_actives'].find({'type_active': type_active}, {'_id': 0}))
    signals = list(db['signals'].find({'access': 'all', 'type_active': type_active}, {'_id': 0}))[0]['signals']

    res = []

    for user_data in users:
        for signal in signals:
            if user_data['active'].lower() == signal['active'].lower():
                res.append({
                    'username': user_data['username'],
                    'active': signal['active'],
                    'interval': signal['interval'],
                    'signals': signal['indicator'],
                    'type_active': type_active
                })

    return res


def update_tg():
    fonds = write_notification('fonds')
    crypto = write_notification('crypto')
    result = fonds + crypto
    for signal in result:
        signal['time_create'] = int(datetime.now().timestamp())
        check_exists = list(db['tg_notifications'].find(
            {'active': signal['active'],
             'interval': signal['interval'],
             'signals': signal['signals']}))
        if check_exists:
            for check in check_exists:
                # если условие срабатывает, значит что сигнал новый

                id_user = db['tg_bot_users'].find_one({'username': signal['username']})
                if id_user:
                    user_id = id_user['user_id']
                else:
                    user_id = None

                if (int(datetime.now().timestamp()) - check['time_create']) > TIMES_DELTA[check['interval']]:
                    db['tg_notifications'].find_one_and_update(
                        {'active': signal['active'],
                         'interval': signal['interval'],
                         'signals': signal['signals']},
                        {'$set': {'time_create': int(datetime.now().timestamp()),
                                  'is_send': False,
                                  'user_id': user_id}}, upsert=True
                    )

        else:
            signal['is_send'] = False
            id_user = db['tg_bot_users'].find_one({'username': signal['username']})
            if id_user:
                signal['user_id'] = id_user['user_id']
            else:
                signal['user_id'] = None

            db['tg_notifications'].insert_one(signal)

    # todo: удалить старые уведомления из этой коллекции


if __name__ == '__main__':
    update_tg()
