import datetime

import numpy as np


class BotIndicators(object):
    def __init__(self, long_prd, short_prd, signal_long_length, signal_short_length=0):
        self.macd = 0
        self.long = long_prd  # long EMA
        self.short = short_prd  # short EMA
        self.signal_long_length = signal_long_length  # signal line EMA
        self.purchase_prices = []
        self.sell_prices = []
        self.signal_short_length = signal_short_length  # for future post
        self.long_signal = []
        self.long_ema = 0
        self.short_ema = 0
        self.diffs = 0

    def MACD(self, prices):
        # use first <long/short> # of points to start the EMA
        # since it depends on previous EMA
        long_sma_data = prices.loc[:self.long - 1]
        short_sma_data = prices.loc[:self.short - 1]
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

        self.short_ema = self.short_ema[(self.long - self.short):]

        # create numpy arrays to easily difference EMAs
        self.long_ema = np.asarray(self.long_ema)
        self.short_ema = np.asarray(self.short_ema)
        self.macd = self.short_ema - self.long_ema

        signal_line_sma = self.movingAverage(self.signal_long_length, self.macd[-self.signal_long_length:])
        self.long_signal = [signal_line_sma]
        # calculate the signal line for the actual (non-EMA) data
        for m in self.macd[self.signal_long_length + 1:]:
            self.long_signal.append(self.ema(self.signal_long_length, m, self.long_signal[-1]))
        # remove first entry in signal since it was only used to start calc
        self.long_signal = self.long_signal[1:]
        self.diffs = self.macd - self.long_signal

        for i in range(1, len(self.diffs)):
            # previous MACD was < signal and current is greater so  buy
            if self.diffs[i - 1] < 0 and self.diffs[i] > 0:
                return 1
            # previous MACD was > signal and current is less so  sell
            if self.diffs[i - 1] > 0 and self.diffs[i] < 0:
                return -1

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
