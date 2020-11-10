import numpy as np


class BotIndicators(object):
    def __init__(self):
        self.MACDLine = []

    def MACD(self, prices, nslow=26, nfast=12):
        twentySixEMA = EMA(prices, nslow)
        twentyFourEMA = EMA(prices, nfast)
        MACDline = twentyFourEMA - twentySixEMA
        self.MACDLine.append(MACDline)
        signalLine = EMA(self.MACDLine, 9)
        return signalLine
        # return twentySixEMA, twentyFourEMA, MACDline


def movingAverage(self, dataPoints, period):
    if (len(dataPoints) > 0):
        return float(sum(dataPoints[-period:]) / float(len(dataPoints[-period:])))


def momentum(self, dataPoints, period=14):
    if (len(dataPoints) > period - 1):
        return dataPoints[-1] * 100 / dataPoints[-period]


def EMA(prices, period):
    x = np.asarray(prices)
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    a = np.convolve(x, weights, mode='full')[:len(x)]
    if len(a) < period:
        a = a[-1]
    else:
        a = a[period]
    return a


def RSI(prices, period=14):
    deltas = np.diff(prices)
    seed = deltas[:period + 1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100. / (1. + rs)

    for i in range(period, len(prices)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)
    if len(prices) > period:
        return rsi[-1]
    else:
        return 50  # output a neutral amount until enough prices in list to calculate RSI
