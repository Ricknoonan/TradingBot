from Utils.botlog import BotLog
from Exchange.Bot.botindicators import BotIndicators
from Exchange.Bot.bottrade import BotTrade
import pandas as pd



class BotStrategy3(object):
    def __init__(self, pair):
        self.output = BotLog()
        self.prices = []
        self.closes = []
        self.trades = {}
        self.maxTradesPerPair = 10
        self.tradeByPair = 0
        self.openTrades = {}
        self.currentPrice = ""
        self.currentClose = ""
        self.accumProfit = 0
        self.closedPosCounter = 0
        self.indicator = BotIndicators(long_prd=26, short_prd=12, signal_long_length=9, )
        self.pair = pair

    def tick(self, price):
        self.currentPrice = float(price)
        self.prices.append(self.currentPrice)
        self.evaluatePositions()

    def evaluatePositions(self):
        priceFrame = pd.DataFrame({'price': self.prices})
        if len(priceFrame) > 12:
            momentum = self.indicator.momentumROC(self.prices)
            rsi = self.indicator.RSI(priceFrame) > 60
            for tradePairKey, trade in self.trades.items():
                if trade.status == "OPEN":
                    self.closeTrade(momentum, rsi, trade)
                    if trade.isClosed():
                        return trade
            if momentum > 20 & (rsi < 40):
                self.trades[self.pair] = (BotTrade(self.currentPrice, 0.1))

    def closeTrade(self, momentum, rsi, trade):
        if (momentum < 0) & (rsi > 60):
            trade.close(self.currentPrice)
            self.accumProfit += trade.profit
            self.closedPosCounter += 1

    def openTrade(self, macd, rsi):
        if len(self.prices) > 35:
            if (macd == 1) & (rsi < 40):
                self.trades[self.pair] = (BotTrade(self.currentPrice, 0.1))


# NOTES
# If underlying prices make a new high or low that isn't
# confirmed by the RSI, this divergence can signal a price reversal.
# If the RSI makes a lower high and then follows with a downside move below
# a previous low, a Top Swing Failure has occurred. If the RSI makes a higher
# low and then follows with an upside move above a previous high, a Bottom
# Swing Failure has occurred.
