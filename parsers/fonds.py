import tinkoff.invest.exceptions
import numpy as np
import warnings
import talib
import mplfinance as mpl
from decouple import config
from datetime import datetime
from pprint import pprint
from pandas import DataFrame, to_datetime
from loguru import logger
from tinkoff.invest import Client, CandleInterval

from database import db_connect
from utils.indicators import ma_indicator, rsi_indicator, triangle_pattern

warnings.filterwarnings("ignore", category=RuntimeWarning)

CLASSES_RU_STOCKS = ['TQBR', 'SPBXM']
# reso minutes - 1 day
# reso hours - 1 week
# reso day/week - 1 year
# reso month - 3 years
INTERVALS = {
    '1m': CandleInterval.CANDLE_INTERVAL_1_MIN,
    '3m': CandleInterval.CANDLE_INTERVAL_3_MIN,
    '5m': CandleInterval.CANDLE_INTERVAL_5_MIN,
    '15m': CandleInterval.CANDLE_INTERVAL_15_MIN,
    '30m': CandleInterval.CANDLE_INTERVAL_30_MIN,
    '1h': CandleInterval.CANDLE_INTERVAL_HOUR,
    '4h': CandleInterval.CANDLE_INTERVAL_4_HOUR,
    '1d': CandleInterval.CANDLE_INTERVAL_DAY,
    '1w': CandleInterval.CANDLE_INTERVAL_WEEK,
    '1M': CandleInterval.CANDLE_INTERVAL_MONTH,
}

TIMEFRAME_INTERVAL = {
    '5m': 86400,  # 1 day
    '30m': 86400 * 5,  # 5 day 240 w
    '1h': 86400 * 12,  # 12 day 288 w
    '4h': 2592000,  # 1 month 180
    '1d': 18144000,  # 7 month 210
    '1w': 62208000,  # 2 years 103
    '1M': 31104000 * 10  # 10 years
}


def get_figi_by_ticker(ticker):
    db = db_connect()

    data = list(db['figi'].find({'ticker': ticker}))
    for elem in data:
        if elem['class_code'] in CLASSES_RU_STOCKS:
            return elem['figi']

    return None


def get_candles_tinkoff(ticker, timeframe_, proxy=None):
    token = config('API_KEY_TINKOFF')
    logger.info(f'get data for {ticker}_{timeframe_}')
    try:
        timeframe = INTERVALS[timeframe_]
        offset = TIMEFRAME_INTERVAL[timeframe_]
    except KeyError:
        logger.error(f'Wrong interval `{timeframe_}`, available: {list(INTERVALS.keys())}')
        return
    figi = get_figi_by_ticker(ticker)
    if not figi:
        logger.error(f'Figi by `{ticker}` not found')
        return
    with Client(token) as client:
        try:
            candle_data = client.market_data.get_candles(
                figi=figi,
                from_=datetime.fromtimestamp(datetime.utcnow().timestamp() - offset),
                to=datetime.utcnow(),
                interval=timeframe,
            )
            candles = candle_data.candles
        except tinkoff.invest.exceptions.RequestError:
            logger.debug(f'Limit of bars warning | offset: {offset} | interval: {timeframe_}')
            candle_data = client.get_all_candles(
                figi=figi,
                from_=datetime.fromtimestamp(datetime.utcnow().timestamp() - offset),
                to=datetime.utcnow(),
                interval=timeframe
            )
            candles = [elem for elem in candle_data]

    if not candles:
        logger.error(f'No data for {ticker} in {timeframe_}')
        return

    df = DataFrame([{
        'time': to_datetime(c.time),
        'volume': c.volume,
        'open': cast_money(c.open),
        'close': cast_money(c.close),
        'high': cast_money(c.high),
        'low': cast_money(c.low),
    } for c in candles])

    return df


def cast_money(v):
    return v.units + v.nano / 1e9


def make_plot(active, timeframe_input, df_candles, df_no_index):
    if df_candles is not None:
       # ma_points_red, ma_points_green = ma_indicator(df_candles)

        #rsi_plot, rsi_high70_plot, rsi_low30_plot, rsi_points_red, rsi_points_green = rsi_indicator(df_candles)

        triangle_lines = triangle_pattern(df_no_index)

        #upper_bollinger_line, lower_bollinger_line, bs_green, bs_red = bollinger_lines(df_candles)

       # print(bs_green)
       #  plots = [
       #      mpl.make_addplot(list(ma_points_red), type='scatter', marker='v', markersize=100, color='red', secondary_y=False),
       #      mpl.make_addplot(ma_points_green, type='scatter', marker='^', markersize=100, color='green',
       #                       secondary_y=False),
       #      mpl.make_addplot(rsi_plot, panel=1, fill_between={'y1': rsi_high70_plot.values,
       #                                                        'y2': rsi_low30_plot.values,
       #                                                        'alpha': 0.3,
       #                                                        'color': '#A6D5FF'}, color='k', width=1,
       #                       secondary_y=False),
       #      mpl.make_addplot(list(rsi_high70_plot), panel=1, color='#A6D5FF', alpha=0.3, secondary_y=False),
       #      mpl.make_addplot(rsi_low30_plot, panel=1, color='#A6D5FF', alpha=0.3, secondary_y=False),
       #      mpl.make_addplot(rsi_points_red, type='scatter', marker='v', markersize=100, color='red', panel=1,
       #                       secondary_y=False),
       #      mpl.make_addplot(rsi_points_green, type='scatter', marker='^', markersize=100, color='green', panel=1,
       #                       secondary_y=False),
       #      # mpl.make_addplot(pivot_dots, type='scatter', marker='.', markersize=200, color='blue', alpha=0.5,
       #      #                 secondary_y=False),
       #
       #      mpl.make_addplot(upper_bollinger_line.tolist(), panel=0, color='r', fill_between={'y1': upper_bollinger_line.tolist(),
       #                                                                               'y2': lower_bollinger_line.values,
       #                                                                               'alpha': 0.3,
       #                                                                               'color': '#A6D5FF'}, alpha=0.5,
       #                       secondary_y=False),
       #      mpl.make_addplot(lower_bollinger_line, panel=0, color='green', alpha=0.4, secondary_y=False),
       #      mpl.make_addplot(bs_green, type='scatter', marker='^', markersize=100, color='green', secondary_y=False),
       #      mpl.make_addplot(bs_red, type='scatter', marker='v', markersize=100, color='red', secondary_y=False),
       #
       #  ]
        result_plot, axis = mpl.plot(df_candles, type='candle',
                                     figsize=(19, 12), style='yahoo',
                                     mav=(5, 12),
                                     tight_layout=True,
                                     ylabel='',
                                     #addplot=plots,
                                     alines={'alines': triangle_lines, },
                                     returnfig=True,
                                     )

        result_plot.savefig(f'../graphics/{active}_{timeframe_input}.png', bbox_inches='tight')
        logger.info('plot saved')


if __name__ == '__main__':
    active = 'AFL'
    tf_in = '1h'
    df_no_index = get_candles_tinkoff(active, timeframe_=tf_in)
    print(df_no_index)
    df_indexed = df_no_index.set_index('time')

    # make_plot(active, tf_in, df_indexed, df_no_index)
