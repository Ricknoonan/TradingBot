import datetime

import numpy as np


class BotIndicators(object):
    def __init__(self, years, long_prd, short_prd, signal_long_length, end_date=None, signal_short_length = 0, column = "Open"):
        self.MACDLine = []
        self.years = years  # number of years in the past to get data
        self.long = long_prd  # long EMA
        self.short = short_prd  # short EMA
        self.signal_long_length = signal_long_length  # signal line EMA
        self.purchase_prices = []
        self.sell_prices = []
        self.end_date = datetime.datetime.today() if (end_date is None) else end_date
        self.signal_short_length = signal_short_length  # for future post
        self.column = column  # column with price data

    def MACD(self, prices, nslow=26, nfast=12):
        # use first <long/short> # of points to start the EMA
        # since it depends on previous EMA
        long_sma_data = prices.loc[:self.long-1]
        short_sma_data = prices.loc[:self.short-1]
        long_sma_value = self.movingAverage(long_sma_data, self.long)
        short_sma_value = self.movingAverage(short_sma_data, self.short)
        long_ema = [long_sma_value]
        short_ema = [short_sma_value]
        # need to remove these values at the end
        # 'use up' the remainder of the data for the EMAs
        for index, v in prices[self.long:].iterrows():
            long_ema.append(self.ema(self.long, v, long_ema[-1]))
        for index, v in prices[self.short:].iterrows():
            short_ema.append(self.ema(self.short, v, short_ema[-1]))

    def movingAverage(self, dataPoints, period):
        if (len(dataPoints) > 0):
            return float(sum(dataPoints[-period:]) / float(len(dataPoints[-period:])))

    def RSI(self, prices, period=14):
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

    def momentum(self, dataPoints, period=14):
        if (len(dataPoints) > period - 1):
            return dataPoints[-1] * 100 / dataPoints[-period]

    def ema(self, N, curr_price, past_ema):
        # "Smoothing Factor"
        k = 2 / (N + 1)
        ema = (curr_price * k) + (past_ema * (1 - k))
        return ema
