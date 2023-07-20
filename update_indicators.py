import datetime
import json
import time

from loguru import logger
from parsers.update_actives import write_actives
from database import db_connect

from utils.update_signals import update_signals
from utils.update_tg_notifications import update_tg
db = db_connect()


if __name__ == '__main__':
    import argparse
    # todo: сделать по интервалам
    parser = argparse.ArgumentParser(description='Update fonds and crypto indicators')
    parser.add_argument('type', type=str, choices=['fonds', 'crypto'])
    args = parser.parse_args()
    proxies = None
    if args.type == 'fonds':
        type_parse = 'fonds'
        # actives = list(db['patterns_app_fondsarray'].find({}, {'_id': 0}))
        # actives_users = list(db['users_actives'].find({'type_active': 'fonds'}, {'_id': 0}))
        # actives_users_list = [active['active'].upper() for active in actives_users]
        # actives_list = [active['name'] for active in actives]
    elif args.type == 'crypto':
        type_parse = 'crypto'
        # proxies = json.load(open('proxies/proxies.json', 'r'))
        # actives = list(db['patterns_app_cryptoarray'].find({}, {'_id': 0}))
        # actives_users = list(db['users_actives'].find({'type_active': 'crypto'}, {'_id': 0}))
        # actives_users_list = [active['active'].upper() for active in actives_users]
        # actives_list = [active['name'] for active in actives]
    else:
        type_parse = None
        actives_list = None
        actives_users_list = None
        logger.error(f'uncorrected attribute {args.type}')
    if type_parse is not None:
        while True:
            f = datetime.datetime.now()

            if type_parse == 'fonds':
                actives = list(db['patterns_app_fondsarray'].find({}, {'_id': 0}))
                actives_users = list(db['users_actives'].find({'type_active': 'fonds'}, {'_id': 0}))
                actives_users_list = [active['active'].upper() for active in actives_users]
                actives_list = [active['name'] for active in actives]
            elif type_parse == 'crypto':
                proxies = json.load(open('proxies/proxies.json', 'r'))
                actives = list(db['patterns_app_cryptoarray'].find({}, {'_id': 0}))
                actives_users = list(db['users_actives'].find({'type_active': 'crypto'}, {'_id': 0}))
                actives_users_list = [active['active'].upper() for active in actives_users]
                actives_list = [active['name'] for active in actives]

            write_actives(actives_list + actives_users_list, type_parse, proxies)
            update_signals(type_parse)
            update_tg()
            s = datetime.datetime.now()
            print(f'Time elapsed: {s - f}')
            time.sleep(600)

