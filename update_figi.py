from decouple import config
from pandas import DataFrame
from tinkoff.invest import Client, InstrumentStatus
from tinkoff.invest.services import InstrumentsService
from loguru import logger

from database import db_connect


def update():
    with Client(config('API_KEY_TINKOFF')) as client:
        instruments: InstrumentsService = client.instruments
        shares = instruments.shares(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments
    shares_df = DataFrame(shares, columns=['name', 'figi', 'ticker', 'class_code'])
    shares_dict = shares_df.to_dict(orient='records')
    db = db_connect()
    db['figi'].drop()
    db['figi'].insert_many(shares_dict)
    logger.info(f'Successfully updated {len(shares_dict)} figi')


if __name__ == '__main__':
    # todo: this script should be executed daily
    #update()
    import yfinance as yf

    data = yf.Ticker("aapl")
    hist = data.history(period="2d", interval='5m')
    print(hist)


