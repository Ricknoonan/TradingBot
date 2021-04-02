import sys, getopt
import time

from Exchange.Bot.botlog import BotLog


class BotCandlestick(object):
    def __init__(self, period=300, open=None, close=None, high=None, low=None, priceAverage=None, date=None):
        self.date = date
        self.current = None
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.startTime = time.time()
        self.period = period
        self.output = BotLog()
        self.priceAverage = priceAverage

    def tick(self, price):
        self.current = float(price)
        if (self.open is None):
            self.open = self.current

        if ((self.high is None) or (self.current > self.high)):
            self.high = self.current

        if ((self.low is None) or (self.current < self.low)):
            self.low = self.current

        if (time.time() >= (self.startTime + self.period)):
            self.close = self.current
            self.priceAverage = (self.high + self.low + self.close) / float(3)

        self.output.logOpen(
            "Open: " + str(self.open) + " Close: " + str(self.close) + " High: " + str(self.high) + " Low: "
            + str(self.low) + " Current: " + str(self.current) + " Start time: " + str(self.date))

    def isClosed(self):
        if (self.close is not None):
            return True
        else:
            return False
