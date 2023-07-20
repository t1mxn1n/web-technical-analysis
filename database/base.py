import pymongo
from decouple import config


def db_connect():
    client = pymongo.MongoClient(config('HOST'))
    db = client[config('DB_NAME')]
    return db
