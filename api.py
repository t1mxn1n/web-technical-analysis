import uvicorn
from fastapi import FastAPI, Response, Query
import random

from database import db_connect
from utils.make_plot import plot, build_plot

app = FastAPI()
db = db_connect()


@app.get('/get_plot')
def get_plot(response: Response, type_active: str = Query(None), active: str = Query(None),
             resolution: str = Query(None), ind_code: str = Query(None)):
    response.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:8000"

    ind = {
        'ma': bool(int(ind_code[0])),
        'rsi': bool(int(ind_code[1])),
        'bollinger': bool(int(ind_code[2])),
        'triangle': bool(int(ind_code[3])),
        'has': bool(int(ind_code[4])),
        'talib': bool(int(ind_code[5]))
    }

    if 'fonds' in active or 'crypto' in active:
        active = active.split('_')[0]

    name = plot(type_active, active, resolution, ind)
    if not name:
        name = build_plot(active, type_active, resolution, ind)

    return {'name': name} if name else {'error': 'not found'}


@app.get('/get_actives')
def get_plot(response: Response, type_active: str = Query(...)):
    response.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:8000"
    if type_active == 'fonds':
        collection = db['patterns_app_fondsarray']
    else:
        collection = db['patterns_app_cryptoarray']

    actives = list(collection.find({}, {'_id': 0}))
    actives_list = [active['name'] for active in actives]
    return {'actives': actives_list}


@app.get('/add_user_active')
def add_user_active(response: Response, type_active: str = Query(...), active: str = Query(...),
                    username: str = Query(None)):
    response.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:8000"
    limit_actives_per_user = 5
    if type_active == 'fonds':
        collection_check = db['figi']
        find_ = {'ticker': active.upper(), 'class_code': {'$in': ['SPBXM', 'TQBR']}}
    else:
        collection_check = db['crypto_symbols']
        find_ = {'symbol': active.upper()}

    res = list(collection_check.find(find_, {'_id': 0}))
    if not res:
        return {'error': 'not found', 'error_type': '0'}

    collection = db['users_actives']
    find_ = {'username': username, 'type_active': type_active}

    res_actives = collection.find(find_, {'_id': 0})
    names_actives = [data['active'] for data in list(res_actives)]

    if active in names_actives:
        return {'error': f'{active} already in list', 'error_type': '1'}

    if res_actives.count() < limit_actives_per_user:
        collection.insert_one({'username': username, 'type_active': type_active, 'active': active})
        return {'added': active.upper(),
                'count': res_actives.count(),
                'left_count': limit_actives_per_user - res_actives.count(),
                'error_type': '-1'}
    else:
        return {'error': f'exceeded limit {limit_actives_per_user}', 'error_type': '2', 'list': names_actives}


@app.get('/get_users_actives')
def get_users_actives(response: Response, username: str = Query(None)):
    response.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:8000"
    collection = db['users_actives']
    actives = list(collection.find({'username': username}, {'_id': 0}))
    if not actives:
        return {'error': 'empty', 'error_type': '0'}
    fonds = [data['active'].upper() for data in actives if data['type_active'] == 'fonds']
    crypto = [data['active'].upper() for data in actives if data['type_active'] == 'crypto']
    return {'fonds': fonds, 'crypto': crypto, 'error_type': '-1'}


@app.get('/delete_user_active')
def delete_user_active(response: Response, type_active: str = Query(...), active: str = Query(...),
                       username: str = Query(None)):
    response.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:8000"
    collection = db['users_actives']

    actives1 = collection.delete_one({'username': username, 'type_active': type_active, 'active': active.lower()})
    actives2 = collection.delete_one({'username': username, 'type_active': type_active, 'active': active.upper()})
    if actives1.deleted_count == 0 and actives2.deleted_count == 0:
        return {'error_type': '0', 'msg': 'not find in db'}
    return {'error_type': '-1', 'msg': 'successful'}
    # fonds = [data['active'].upper() for data in actives if data['type_active'] == 'fonds']
    # crypto = [data['active'].upper() for data in actives if data['type_active'] == 'crypto']
    # return {'fonds': fonds, 'crypto': crypto, 'error_type': '-1'}


@app.get('/get_public_signals')
def get_public_signals(response: Response, type_active: str = Query(None)):
    response.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:8000"
    collection = db['signals']
    signals = list(collection.find({'type_active': type_active, 'access': 'public'}, {'_id': 0}))
    if not signals:
        return {'error': 'empty', 'error_type': '0'}
    return {'signals': signals}


@app.get('/get_user_tg_code')
def get_user_tg_code(response: Response, username: str = Query(None)):
    response.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:8000"
    collection = db['tg_bot_users']
    user_data = collection.find_one({'username': username})
    if not user_data:
        set_data = {
            'code': str(random.randint(1000, 9999)),
        }
        collection.find_one_and_update({'username': username}, {'$set': set_data}, upsert=True)
        return {'username': username, 'code': set_data['code']}
    return {'username': username, 'code': user_data['code']}


if __name__ == "__main__":
    uvicorn.run('api:app', host='127.0.0.1', port=8080, reload=True)
