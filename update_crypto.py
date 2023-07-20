from database import db_connect


def update():
    db = db_connect()
    collection = db['crypto_symbols']
    collection_insert = db['patterns_app_cryptoarray']
    sorted_symbols = collection.find({}, sort=[('volume_usdt', -1)])

    collection_insert.delete_many({'added': 'by_volume'})

    for token in list(sorted_symbols)[0:15]:
        collection_insert.find_one_and_update({'name': token['symbol']},
                                              {'$set': {'name': token['symbol'], 'added': 'by_volume'}},
                                              upsert=True)


if __name__ == '__main__':
    update()
