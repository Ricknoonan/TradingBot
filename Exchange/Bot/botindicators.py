import datetime

import numpy as np
import pandas as pd

from Exchange.Bot.botlog import BotLog


class BotIndicators(object):
    def __init__(self, long_prd, short_prd, signal_long_length, signal_short_length=0):
        self.macd = []
        self.output = BotLog()
        self.long = long_prd  # long EMA
        self.short = short_prd  # short EMA
        self.signal_long_length = signal_long_length  # signal line EMA
        self.purchase_prices = []
        self.sell_prices = []
        self.signal_short_length = signal_short_length  # for future post
        self.long_signal = []
        self.long_ema = 0
        self.short_ema = []
        self.diffs = []

    def MACD(self, priceFrame):
        # use first <long/short> # of points to start the EMA
        # since it depends on previous EMA
        long_sma_data = priceFrame.loc[:self.long - 1]['price']
        short_sma_data = priceFrame.loc[:self.short - 1]['price']
        long_sma_value = self.movingAverage(long_sma_data, self.long)
        short_sma_value = self.movingAverage(short_sma_data, self.short)
        long_ema = [long_sma_value]
        short_ema = [short_sma_value]

        for index, v in priceFrame[-self.long:].iterrows():
            long_ema.append(self.ema(self.long, v['price'], long_ema[-1]))
        for index, v in priceFrame[-self.short:].iterrows():
            short_ema.append(self.ema(self.short, v['price'], short_ema[-1]))

        self.macd.append(short_ema[-1] - long_ema[-1])

        if len(self.macd) > self.signal_long_length:
            signal_line_sma = self.movingAverage(self.macd[-self.signal_long_length:], self.signal_long_length)
            self.long_signal = [signal_line_sma]
            for m in self.macd[-self.signal_long_length:]:
                self.long_signal.append(self.ema(self.signal_long_length, m, self.long_signal[-1]))
            self.long_signal = self.long_signal[1:]
            self.diffs.append(self.macd[-1] - self.long_signal[-1])
            if len(self.diffs) > 2:
                # previous MACD was < signal and current is greater so  buy
                if self.diffs[-2] < 0 and self.diffs[-1] > 0:
                    return 1
                # previous MACD was > signal and current is less so  sell
                if self.diffs[-2] > 0 and self.diffs[-1] < 0:
                    return -1

    def movingAverage(self, dataPoints, period):
        if (len(dataPoints) > 0):
            return sum(dataPoints) / period

    def RSI(self, prices, period=24):
        array = prices['price'].to_numpy()
        deltas = np.diff(array)
        seed = deltas[-period:]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down
        rsi = 100. - (100. / (1. + rs))
        #
        # for i in range(period, len(prices)):
        #     delta = deltas[i - 1]  # cause the diff is 1 shorter
        #     if delta > 0:
        #         upval = delta
        #         downval = 0.
        #     else:
        #         upval = 0.
        #         downval = -delta
        #
        #     up = (up * (period - 1) + upval) / period
        #     down = (down * (period - 1) + downval) / period
        #     rs = up / down
        #     rsi[i] = 100. - 100. / (1. + rs)
        if len(prices) > period:
            return rsi
        else:
            return 50  # output a neutral amount until enough prices in list to calculate RSI

    def momentumROC(self, dataPoints, period=12):
        if len(dataPoints) > period - 1:
            return dataPoints[-1] * 100 / dataPoints[-period]

    def ema(self, N, curr_price, past_ema):
        # "Smoothing Factor"
        k = 2 / (N + 1)
        ema = (curr_price * k) + (past_ema * (1 - k))
        return ema
