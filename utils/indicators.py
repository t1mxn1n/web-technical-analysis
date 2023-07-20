import numpy as np
import talib
from scipy.stats import linregress


def ma_indicator(candles):
    candles['MA5'] = candles['close'].rolling(5).mean()
    candles['MA12'] = candles['close'].rolling(12).mean()

    ma5 = candles['MA5'].to_numpy()
    ma12 = candles['MA12'].to_numpy()
    signal_indexes = np.argwhere(np.diff(np.sign(ma5 - ma12))).flatten()
    signals = candles['close'].iloc[signal_indexes].to_dict()

    # todo: заменить двумя строчками из np, как для линий боллинджера

    red_signal = []
    green_signal = []
    for index, row in candles.iterrows():
        if index in signals and not np.isnan(row['MA12']):
            if row['MA5'] > row['MA12']:
                red_signal.append(row['MA5'])
                green_signal.append(np.nan)
            else:
                green_signal.append(row['MA5'])
                red_signal.append(np.nan)
        else:
            red_signal.append(np.nan)
            green_signal.append(np.nan)

    return candles['MA5'], candles['MA12'], red_signal, green_signal


def rsi_indicator(candles):
    candles['RSI'] = talib.RSI(candles['close'], timeperiod=14)
    rsi = candles['RSI']
    rsi_up_data = rsi.replace(to_replace=rsi.values, value=70)
    rsi_down_data = rsi.replace(to_replace=rsi.values, value=30)

    rsi = rsi.to_numpy()
    line70 = rsi_up_data.to_numpy()
    line30 = rsi_down_data.to_numpy()
    signal_indexes_red = np.argwhere(np.diff(np.sign(rsi - line70))).flatten()
    signal_indexes_green = np.argwhere(np.diff(np.sign(rsi - line30))).flatten()
    signals_red = candles['close'].iloc[signal_indexes_red].to_dict()
    signals_green = candles['close'].iloc[signal_indexes_green].to_dict()
    red_signal = []
    green_signal = []
    for index, row in candles.iterrows():
        if index in signals_red and not np.isnan(row['RSI']):
            if row['RSI'] < 70:
                red_signal.append(80)
                green_signal.append(np.nan)
                continue
            else:
                green_signal.append(np.nan)
                red_signal.append(np.nan)
                continue
        if index in signals_green and not np.isnan(row['RSI']):
            if row['RSI'] > 30:
                green_signal.append(20)
                red_signal.append(np.nan)
                continue
            else:
                green_signal.append(np.nan)
                red_signal.append(np.nan)
                continue
        else:
            red_signal.append(np.nan)
            green_signal.append(np.nan)

    return rsi, rsi_up_data, rsi_down_data, red_signal, green_signal


def pivot_id(df, candle, left_offset, right_offset):
    # обработка граничных значений
    if candle - left_offset < 0 or candle + right_offset >= len(df):
        return 0
    pivot_low = 1
    pivot_high = 1
    for i in range(candle - left_offset, candle + right_offset + 1):
        if df.low[candle] > df.low[i]:
            pivot_low = 0
        if df.high[candle] < df.high[i]:
            pivot_high = 0
    if pivot_low and pivot_high:
        return 3
    elif pivot_low:
        return 1
    elif pivot_high:
        return 2
    else:
        return 0


def pointpos(x, field_name, p=None):
    if not p:
        p = 0.002
    if x[field_name] == 1:
        return x['low'] - x['low'] * p
    elif x[field_name] == 2:
        return x['high'] + x['high'] * p
    else:
        return np.nan


def slope_numbers_division(price):
    if price > 1:
        price = int(price)
        return len(str(price)) - 2
    else:
        c = 0
        while price < 1:
            price = price * 10
            c += 1
        return c


def h_and_s(df):
    df['long_pivot'] = df.apply(lambda x: pivot_id(df, x.name, 15, 15), axis=1)
    df['short_pivot'] = df.apply(lambda x: pivot_id(df, x.name, 4, 4), axis=1)
    df['long_pointpos'] = df.apply(lambda row: pointpos(row, 'long_pivot', 0.003), axis=1)
    df['short_pointpos'] = df.apply(lambda row: pointpos(row, 'short_pivot'), axis=1)
    vlines = []
    support_lines = []
    back_candles = 15
    for candleid in range(back_candles, len(df) - back_candles):
        if df.iloc[candleid].long_pivot != 2 or df.iloc[candleid].short_pivot != 2:
            continue

        maxim = np.array([])
        minim = np.array([])
        xxmin = np.array([])
        xxmax = np.array([])
        minbcount = 0  # minimas before head
        maxbcount = 0  # maximas before head
        minacount = 0  # minimas after head
        maxacount = 0  # maximas after head

        for i in range(candleid - back_candles, candleid + back_candles):
            if df.iloc[i].short_pivot == 1:
                minim = np.append(minim, df.iloc[i].low)
                xxmin = np.append(xxmin, i)  # could be i instead df.iloc[i].name
                if i < candleid:
                    minbcount = +1
                elif i > candleid:
                    minacount += 1
            if df.iloc[i].short_pivot == 2:
                maxim = np.append(maxim, df.iloc[i].high)
                xxmax = np.append(xxmax, i)  # df.iloc[i].name
                if i < candleid:
                    maxbcount += 1
                elif i > candleid:
                    maxacount += 1

        if minbcount < 1 or minacount < 1 or maxbcount < 1 or maxacount < 1:
            continue

        slmin, intercmin, rmin, pmin, semin = linregress(xxmin, minim)
        headidx = np.argmax(maxim, axis=0)

        a = slope_numbers_division(df.iloc[candleid].close)

        if df.iloc[candleid].close > 1:
            slmin_check = slmin / 10**a
        else:
            slmin_check = slmin * 10**a

        if ((maxim[headidx] - maxim[headidx - 1]) / maxim[headidx - 1] > 0.0015) and \
                ((maxim[headidx] - maxim[headidx + 1]) / maxim[headidx + 1] > 0.0015) and \
                abs(slmin_check) <= 0.06:
            l1 = df.iloc[candleid - back_candles].time
            l2 = df.iloc[candleid + back_candles].time
            support_lines.append(has_line(df, xxmin, slmin, intercmin, candleid, back_candles))
            vlines.append(l1)
            vlines.append(l2)

            continue

    remove_intersections_has(vlines, support_lines)
    return vlines, support_lines


def remove_intersections_has(vlines, support_lines):

    for sup_line in support_lines:
        start_1 = sup_line[0][0]
        finish_1 = sup_line[1][0]
        for check_line in support_lines:
            if sup_line == check_line:
                continue
            start_2 = check_line[0][0]
            finish_2 = check_line[1][0]
            if start_2 < start_1 and start_2 < finish_1:
                vlines.remove(start_2)
                vlines.remove(finish_2)
                support_lines.remove(check_line)


def has_line(df, xxmin, slmin, intercmin, candle_id, back_candles):
    left_border = candle_id - back_candles
    right_border = candle_id + back_candles
    temp_line = []
    xxmin[-1] = right_border
    xxmin[0] = left_border
    coordx = df.iloc[xxmin]['time'].to_list()
    y = slmin * xxmin + intercmin
    temp_line.append((coordx[0], y[0]))
    temp_line.append((coordx[-1], y[-1]))
    return temp_line


def detect_addition(df, slope, xx):
    addition = 12
    # todo: сделать отрезки более гибкими, чтобы не было длинных хвостов
    if (int(xx) + addition) >= df.shape[0]:
        addition = df.shape[0] - int(xx) - 1
    return addition

    # if abs(slope) <= 0.03:
    #     return 13
    # elif abs(slope) <= 0.18:
    #     return 5
    # else:
    #     return 0


def prepare_lines_triangle(df, xxmin, slmin, intercmin, xxmax, slmax, intercmax):
    temp_bottom_line = []
    temp_top_line = []

    addition = detect_addition(df, ' ', xxmin[-1])

    # print(xxmin[-1])
    # print(df.shape[0])
    # print(addition)
    xxmin[-1] = xxmin[-1] + addition

    coordx = df.iloc[xxmin]['time'].to_list()
    y = slmin * xxmin + intercmin

    temp_bottom_line.append((coordx[0], y[0], slmin))
    temp_bottom_line.append((coordx[-1], y[-1], slmin))
    addition = detect_addition(df, ' ', xxmax[-1])

    xxmax[-1] = xxmax[-1] + addition

    coordx = df.iloc[xxmax]['time'].to_list()

    y = slmax * xxmax + intercmax

    temp_top_line.append((coordx[0], y[0], slmax))
    temp_top_line.append((coordx[-1], y[-1], slmax))

    return [temp_bottom_line, temp_top_line]


def triangle_pattern(df):
    df['pivot'] = df.apply(lambda x: pivot_id(df, x.name, 3, 3), axis=1)
    df['pointpos'] = df.apply(lambda row: pointpos(row, 'pivot'), axis=1)
    pivot = df['pointpos'].to_list()

    backcandles = 20
    lines = []
    temp_points = []
    for candleid in range(backcandles, len(df)):
        maxim = np.array([])
        minim = np.array([])
        xxmin = np.array([])
        xxmax = np.array([])
        for i in range(candleid - backcandles, candleid + 1):
            if df.iloc[i].pivot == 1:
                minim = np.append(minim, df.iloc[i].low)
                xxmin = np.append(xxmin, i)
            if df.iloc[i].pivot == 2:
                maxim = np.append(maxim, df.iloc[i].high)
                xxmax = np.append(xxmax, i)

        if (xxmax.size < 3 and xxmin.size < 3) or xxmax.size == 0 or xxmin.size == 0:
            continue

        slmin, intercmin, rmin, pmin, semin = linregress(xxmin, minim)
        slmax, intercmax, rmax, pmax, semax = linregress(xxmax, maxim)

        if abs(rmax) >= 0.7 and abs(rmin) >= 0.7 and abs(slmin) <= 0.00001 and slmax < -0.0001:

            x1 = [int(point) for point in xxmin.tolist()]
            x2 = [int(point) for point in xxmax.tolist()]
            if [x1, x2] not in temp_points:
                print('first (нисходящий)')
                lines.extend(prepare_lines_triangle(df, xxmin, slmin, intercmin, xxmax, slmax, intercmax))
                temp_points.append([x1, x2])
            continue
        if abs(rmax) >= 0.7 and abs(rmin) >= 0.7 and slmin >= 0.0001 and abs(slmax) <= 0.00001:

            x1 = [int(point) for point in xxmin.tolist()]
            x2 = [int(point) for point in xxmax.tolist()]
            if [x1, x2] not in temp_points:
                print('second (восходящий)')
                lines.extend(prepare_lines_triangle(df, xxmin, slmin, intercmin, xxmax, slmax, intercmax))
                temp_points.append([x1, x2])
            continue
        if abs(rmax) >= 0.9 and abs(rmin) >= 0.9 and slmin >= 0.0001 and slmax <= -0.0001:

            x1 = [int(point) for point in xxmin.tolist()]
            x2 = [int(point) for point in xxmax.tolist()]
            if [x1, x2] not in temp_points:
                # logger.debug('Симметричный треугольник')
                lines.extend(prepare_lines_triangle(df, xxmin, slmin, intercmin, xxmax, slmax, intercmax))
                temp_points.append([x1, x2])
            continue

    lines = delete_intersections(lines)

    return lines


def get_attributes_from_points_list(points, iteration):
    a = (points[iteration][0][0], points[iteration][0][1])
    b = (points[iteration][1][0], points[iteration][1][1])
    slope = points[iteration][1][2]
    return a, b, slope


def find_intersections(comparable, type_of_lines):
    i = 0
    indexes_to_remove = []
    while i != len(comparable):
        a1, b1, slope1 = get_attributes_from_points_list(comparable, i)
        j = 0
        while j != len(comparable):
            if i == j:
                j += 1
                continue
            a2, b2, slope2 = get_attributes_from_points_list(comparable, j)
            if (a1[0] < a2[0] < b1[0]) or (a1[0] < b2[0] < b1[0]) or (a1[0] < a2[0] and b1[0] > b2[0]):
                if slope1 > slope2:
                    indexes_to_remove.append(j)
                else:
                    indexes_to_remove.append(i)
            j += 1
        i += 1
    indexes_to_remove = list(set(indexes_to_remove))
    comparable = [i for j, i in enumerate(comparable) if j not in indexes_to_remove]
    res = []
    for i in range(len(comparable)):
        first_point = (comparable[i][0][0], comparable[i][0][1])
        second_coint = (comparable[i][1][0], comparable[i][1][1])
        res.append([first_point, second_coint])
    return res


def delete_intersections(lines):
    bottom_lines = [line for index, line in enumerate(lines) if index % 2 == 0]
    top_lines = [line for index, line in enumerate(lines) if index % 2 != 0]
    res = []
    res.extend(find_intersections(bottom_lines, 'bottom'))
    res.extend(find_intersections(top_lines, 'top'))
    return res


def bollinger_lines(df):
    df['SMA_bollinger'] = df['close'].rolling(20).mean()
    df['stddev'] = df['close'].rolling(20).std()
    df['Upper_bollinger_line'] = df['SMA_bollinger'] + 2 * df['stddev']
    df['Lower_bollinger_line'] = df['SMA_bollinger'] - 2 * df['stddev']
    df['Long_signal'] = np.where(df['Lower_bollinger_line'] > df['close'], df['close'], np.nan)
    df['Short_signal'] = np.where(df['Upper_bollinger_line'] < df['close'], df['close'], np.nan)
    return df['Upper_bollinger_line'], df['Lower_bollinger_line'], df['Long_signal'].to_list(), df['Short_signal'].to_list()


def talib_indicators(df):
    open = df['open']
    high = df['high']
    low = df['low']
    close = df['close']
    threeLineStrike = talib.CDL3LINESTRIKE(open, high, low, close)
    threeBlackCrow = talib.CDL3BLACKCROWS(open, high, low, close)
    eveningStar = talib.CDLEVENINGSTAR(open, high, low, close)
    engulfing = talib.CDLENGULFING(open, high, low, close)
    dragonflyDoji = talib.CDLDRAGONFLYDOJI(open, high, low, close)
    gravestoneDoji = talib.CDLGRAVESTONEDOJI(open, high, low, close)
    tasukigap = talib.CDLTASUKIGAP(open, high, low, close)
    hammer = talib.CDLHAMMER(open, high, low, close)
    darkCloudCover = talib.CDLDARKCLOUDCOVER(open, high, low, close)
    piercingLine = talib.CDLPIERCING(open, high, low, close)
    df['3 Line Strike'] = threeLineStrike
    df['3 Black Crow'] = threeBlackCrow
    df['Evening Star'] = eveningStar
    df['Engulfing'] = engulfing
    df['Dragonfly Doji'] = dragonflyDoji
    df['Gravestone Doji'] = gravestoneDoji
    df['Tasuki Gap'] = tasukigap
    df['Hammer'] = hammer
    df['DarkCloudCover'] = darkCloudCover
    df['Piercing Line'] = piercingLine
    topCandles = ["3 Line Strike", "3 Black Crow", "Evening Star", "Engulfing", "Dragonfly Doji", "Gravestone Doji",
                  "Tasuki Gap", "Hammer", "DarkCloudCover", "Piercing Line"]
    green = []
    red = []
    df['indicators'] = 0
    for x in df.index:
        for cd in topCandles:
            if df.loc[x, cd] == 100:
                df.loc[x, 'indicators'] = 100
            elif df.loc[x, cd] == -100:
                df.loc[x, 'indicators'] = -100
            else:
                if df.loc[x, 'indicators'] != 100 and df.loc[x, 'indicators'] != -100:
                    df.loc[x, 'indicators'] = 0
        if df.loc[x, 'indicators'] == 100:
            green.append(df.loc[x, 'low'] - df.loc[x, 'low'] * 0.0022)
            red.append(np.nan)
        elif df.loc[x, 'indicators'] == -100:
            red.append(df.loc[x, 'high'] + df.loc[x, 'high'] * 0.0022)
            green.append(np.nan)
        else:
            red.append(np.nan)
            green.append(np.nan)

    return green, red
