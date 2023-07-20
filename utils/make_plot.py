import pprint
import json
import pandas as pd
import pymongo
import mplfinance as mpl
from matplotlib import MatplotlibDeprecationWarning
from datetime import datetime
import warnings
from pandas import to_datetime
from loguru import logger

from parsers.update_actives import write_actives

TIMEFRAME_PERIODS = {
    '5m': 1800,
    '30m': 1800,
    '1h': 3600,
    '4h': 14400,
    '1d': 86400,
    '1w': 604800,
    '1M': 604800
}

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=MatplotlibDeprecationWarning)

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['patterns']


def build_plot(active, type_active, interval, indicators):
    if type_active == 'fonds':
        proxies = None
    else:
        proxies = json.load(open('proxies/proxies.json', 'r'))
    write_actives([active], type_active, proxies, [interval])
    return plot(type_active, active, interval, indicators)


def plot(type_active, active, interval, indicators: dict):
    collection = db[type_active]

    df = collection.find_one({'name': active, 'interval': interval})

    if df is None:
        return None

    if int(datetime.now().timestamp()) - df['time_update'] > TIMEFRAME_PERIODS[interval]:
        return None

    df_indexed = pd.DataFrame(df['plot_df'])
    df_indexed['time'] = to_datetime(df_indexed['time'])
    df_indexed.set_index('time', inplace=True)
    triangle_lines = []
    plots = []
    name_indicators = ['0', '0', '0', '0', '0', '0']
    legend_names = []
    addition = 0
    vlines = df['indicators']['has'][0]
    from matplotlib.markers import CARETUP, CARETDOWN
    if indicators['ma']:
        name_indicators[0] = '1'
        plots.extend([
            mpl.make_addplot(df['indicators']['ma'][0], type='line', color='orange', alpha=0.5,
                             secondary_y=False),
            mpl.make_addplot(df['indicators']['ma'][1], type='line', color='blue', alpha=0.5,
                             secondary_y=False),
            mpl.make_addplot(df['indicators']['ma'][3], type='scatter', marker='^', markersize=100, color='green',
                             secondary_y=False),
            mpl.make_addplot(df['indicators']['ma'][2], type='scatter', marker='v', markersize=100, color='red',
                             secondary_y=False)
        ])

        legend_names.append('MA5')
        legend_names.append('MA12')
        legend_names.append('MA LONG')
        legend_names.append('MA SHORT')

    if indicators['rsi']:
        name_indicators[1] = '1'
        plots.extend(
            [
                mpl.make_addplot(df['indicators']['rsi'][0], panel=1, color='k', width=1, secondary_y=False),
                mpl.make_addplot(df['indicators']['rsi'][4], type='scatter', marker='^', markersize=100, color='green',
                                 panel=1,
                                 secondary_y=False),
                mpl.make_addplot(df['indicators']['rsi'][3], type='scatter', marker='v', markersize=100, color='red',
                                 panel=1,
                                 secondary_y=False),
                mpl.make_addplot(df['indicators']['rsi'][1], panel=1, color='#A6D5FF', alpha=0.3, secondary_y=False),
                mpl.make_addplot(df['indicators']['rsi'][2], panel=1, color='#A6D5FF',
                                 fill_between={'y1': df['indicators']['rsi'][1],
                                               'y2': df['indicators']['rsi'][2],
                                               'alpha': 0.3,
                                               'color': '#A6D5FF'}, alpha=0.3, secondary_y=False)

            ])
        # legend_names.append('RSI')
        # legend_names.append('RSI30')
        # legend_names.append('RSI70')
        # legend_names.append('RSI SHORT')
        # legend_names.append('RSI LONG')
    # if indicators['triangle']:
    #     name_indicators[2] = '1'
        # todo: преобразование типов данных к pandas datetime

    if indicators['talib']:
        name_indicators[5] = '1'
        plots.extend([
            mpl.make_addplot(df['indicators']['talib'][0], type='scatter', marker='$L$', markersize=100, color='green',
                             secondary_y=False),
            mpl.make_addplot(df['indicators']['talib'][1], type='scatter', marker='$S$', markersize=100, color='red',
                             secondary_y=False)
        ])
        legend_names.append('LONG POSITION')
        legend_names.append('SHORT POSITION')

    if indicators['bollinger']:
        name_indicators[3] = '1'
        plots.extend([
            mpl.make_addplot(df['indicators']['bollinger'][0], panel=0, color='r',
                             alpha=0.5,
                             secondary_y=False),
            mpl.make_addplot(df['indicators']['bollinger'][1], panel=0, color='green', alpha=0.4, secondary_y=False),
            mpl.make_addplot(df['indicators']['bollinger'][3], type='scatter', marker='^', markersize=100,
                             color='green', secondary_y=False),
            mpl.make_addplot(df['indicators']['bollinger'][2], type='scatter',
                             fill_between={'y1': df['indicators']['bollinger'][0],
                                           'y2': df['indicators']['bollinger'][1],
                                           'alpha': 0.3,
                                           'color': '#A6D5FF'}, marker='v', markersize=100, color='red',
                             secondary_y=False),
        ])
        legend_names.append('BOLLINGER UPPER LINE')
        legend_names.append('BOLLINGER BOTTOM LINE')
        legend_names.append('BOLLINGER LONG INDICATOR')
        legend_names.append('BOLLINGER SHORT INDICATOR')

    flag_has = False
    sup_lines = None
    condition_lines = 0
    if indicators['triangle']:
        name_indicators[2] = '1'
        condition_lines = 1
        triangle_lines = df['indicators']['triangle']
        if triangle_lines:
            # addition += 1
            legend_names.insert(0, 'TRIANGLE PATTERN')
    if indicators['has']:
        condition_lines = 2
        flag_has = True
        name_indicators[4] = '1'
        sup_lines = df['indicators']['has'][1]
        if sup_lines:
            # addition += 1
            legend_names.insert(0, 'Голова и плечи')
    if indicators['triangle'] and indicators['has']:
        condition_lines = 3
        if 'Голова и плечи' in legend_names:
            legend_names.remove('Голова и плечи')
        if 'TRIANGLE PATTERN' in legend_names:
            legend_names.remove('TRIANGLE PATTERN')
        # if sup_lines:
        #     legend_names.insert(0, 'Голова и плечи')
        # if triangle_lines:
        #     legend_names.insert(0, 'TRIANGLE PATTERN')
    has_trig_flag = False
    if condition_lines == 1:
        # triangle
        if triangle_lines:
            graphic, axis = mpl.plot(df_indexed, type='candle',
                                     figsize=(14, 8), style='yahoo',
                                     axtitle='Не является индивидуальной инвестиционной рекомендацией',
                                     tight_layout=True,
                                     ylabel='',
                                     addplot=plots,
                                     alines={'alines': triangle_lines, 'alpha': 0.5, 'colors': 'blue'},
                                     returnfig=True,
                                     )
        else:
            graphic, axis = mpl.plot(df_indexed, type='candle',
                                     figsize=(14, 8), style='yahoo',
                                     axtitle='Не является индивидуальной инвестиционной рекомендацией',
                                     tight_layout=True,
                                     ylabel='',
                                     addplot=plots,
                                     returnfig=True,
                                     )

    elif condition_lines == 2:
        # has
        if sup_lines:
            graphic, axis = mpl.plot(df_indexed, type='candle', figsize=(14, 8), style='yahoo', axtitle='Не является индивидуальной инвестиционной рекомендацией', tight_layout=True, ylabel='', vlines={'vlines': vlines, 'alpha': 0.5, 'colors': 'black'}, alines={'alines': df['indicators']['has'][1], 'alpha': 0.5, 'colors': 'black'}, addplot=plots, returnfig=True,)
        else:
            graphic, axis = mpl.plot(df_indexed, type='candle',
                                     figsize=(14, 8), style='yahoo',
                                     axtitle='Не является индивидуальной инвестиционной рекомендацией',
                                     tight_layout=True,
                                     ylabel='',
                                     addplot=plots,
                                     returnfig=True,
                                     )
    elif condition_lines == 3:
        # triangle and has
        has_trig_flag = True
        colors = ['black'] * len(df['indicators']['has'][1])
        colors.extend(['blue'] * len(triangle_lines))
        if not sup_lines and not triangle_lines:
            graphic, axis = mpl.plot(df_indexed, type='candle',
                                     figsize=(14, 8), style='yahoo',
                                     axtitle='Не является индивидуальной инвестиционной рекомендацией',
                                     tight_layout=True,
                                     ylabel='',
                                     addplot=plots,
                                     returnfig=True,
                                     )
        else:
            graphic, axis = mpl.plot(df_indexed, type='candle',
                                     figsize=(14, 8), style='yahoo',
                                     axtitle='Не является индивидуальной инвестиционной рекомендацией',
                                     tight_layout=True,
                                     ylabel='',
                                     vlines={'vlines': vlines, 'alpha': 0.5, 'colors': 'black'},
                                     alines={'alines': df['indicators']['has'][1] + triangle_lines, 'alpha': 0.5,
                                             'colors': colors},
                                     addplot=plots,
                                     returnfig=True,
                                     )
    else:
        # empty
        graphic, axis = mpl.plot(df_indexed, type='candle',
                                 figsize=(14, 8), style='yahoo',
                                 axtitle='Не является индивидуальной инвестиционной рекомендацией',
                                 tight_layout=True,
                                 ylabel='',
                                 addplot=plots,
                                 returnfig=True,
                                 )

    axis[0].legend([None] * (len(plots) + 2))
    handles = axis[0].get_legend().legendHandles

    start_index = 2 if not flag_has or not sup_lines else 3
    start_index = 4 if has_trig_flag else start_index
    start_index = 2 if not sup_lines and not triangle_lines else start_index
    axis[0].legend(handles=handles[start_index:],
                   labels=legend_names,
                   loc='upper left')
    if type_active == 'fonds':
        axis[0].set_ylabel("Цена в ₽")
    else:
        axis[0].set_ylabel("Цена в $")
    if name_indicators[1] == '1':
        axis[2].set_ylabel('Осциллятор RSI')
        axis[2].legend([None] * (len(plots) + 2))
        handles = axis[2].get_legend().legendHandles
        axis[2].legend(handles=handles, labels=['RSI', 'RSI LONG', 'RSI SHORT'], loc='center left')
    name_indicators = ''.join(name_indicators)
    name_image = f'{active}_{interval}_{name_indicators}.png'
    graphic.savefig(f'graphics/{name_image}', bbox_inches='tight')
    logger.info('plot saved')
    return name_image


if __name__ == '__main__':
    ind = {'ma': True,
           'rsi': True,
           'triangle': True,
           'bollinger': True}

    a = plot('fonds', 'SBERP', '1d', ind)

    print(a)
