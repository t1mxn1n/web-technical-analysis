from decouple import config

USE_DATABASE = f'USE {config("DB_NAME")};'
CREATE_DATABASE = f'CREATE DATABASE IF NOT EXISTS {config("DB_NAME")};'
CREATE_TABLE_FIGI = ('CREATE TABLE IF NOT EXISTS figi ('
                     'id int AUTO_INCREMENT, '
                     'figi_value varchar(32), '
                     'name varchar(128), '
                     'ticker varchar(32), '
                     'class_code varchar(32),'
                     'PRIMARY KEY (id));')
DROP_FIGI = 'DROP TABLE IF EXISTS figi;'
INSERT_FIGI = 'INSERT INTO figi (figi_value, name, ticker, class_code) VALUES (%s, %s, %s, %s);'

GET_FIGI_BY_TICKER = 'SELECT figi_value, name, class_code FROM figi WHERE ticker = %s;'
