from Utils.botlog import BotLog
from Exchange.Bot.botindicators import BotIndicators
from Exchange.Bot.bottrade import BotTrade
import numpy as np
import pandas as pd


class BotStrategy(object):
    def __init__(self, pair):
        self.output = BotLog()
        self.prices = []
        self.closes = []
        self.trades = {}
        self.maxTradesPerPair = 1
        self.tradeByPair = 0
        self.openTrades = {}
        self.currentPrice = ""
        self.currentClose = ""
        self.accumProfit = 0
        self.closedPosCounter = 0
        self.indicator = BotIndicators(long_prd=26, short_prd=12, signal_long_length=9, )
        self.pair = pair
        self.MACDIndicator = False

    def tick(self, price):
        self.currentPrice = float(price)
        self.prices.append(self.currentPrice)
        return self.evaluatePositions()

    def evaluatePositions(self):
        priceFrame = pd.DataFrame({'price': self.prices})
        if len(priceFrame) > 24:
            macd = self.indicator.MACD(priceFrame)
            rsi = self.indicator.RSI(priceFrame)
            for tradePairKey, trade in self.trades.items():
                if trade.status == "OPEN":
                    self.closeTrade(macd, rsi, trade)
                    return trade
            for v in self.trades:
                if v == self.pair:
                    self.tradeByPair = self.tradeByPair + 1
            if macd is not None:
                self.setMACD(macd)
                if rsi != 0 & self.tradeByPair <= self.maxTradesPerPair:
                    self.openTrade(rsi)

    def closeTrade(self, macd, rsi, trade):
        if (macd == -1) & (rsi > 60):
            trade.close(self.currentPrice)
            self.accumProfit += trade.profit
            self.closedPosCounter += 1
            self.output.logClose(
                "Entry Price: " + str(trade.entryPrice) + " Status: " + trade.status + " Exit Price: " + str(
                    trade.exitPrice) + " P/L: " + str(trade.profit) + "\n" + "Strategy P/L: " + str(self.accumProfit))

    def openTrade(self, rsi):
        if len(self.prices) > 35:
            if self.MACDIndicator & (rsi < 40):
                self.trades[self.pair] = (BotTrade(self.currentPrice, 0.1))

    def setMACD(self, macd):
        if macd > 0:
            self.MACDIndicator = True
        if macd < 0:
            self.MACDIndicator = False
# NOTES
# If underlying prices make a new high or low that isn't
# confirmed by the RSI, this divergence can signal a price reversal.
# If the RSI makes a lower high and then follows with a downside move below
# a previous low, a Top Swing Failure has occurred. If the RSI makes a higher
# low and then follows with an upside move above a previous high, a Bottom
# Swing Failure has occurred.
