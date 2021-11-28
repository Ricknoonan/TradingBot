from Utils.botlog import BotLog
from Exchange.Bot.botindicators import BotIndicators
from Exchange.Bot.bottrade import BotTrade


class BotStrategy2(object):
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
        self.strategyPnL = 0

    def tick(self, candlestick):
        self.currentPrice = float(candlestick.priceAverage)
        self.prices.append(self.currentPrice)
        self.evaluatePositions()

    def evaluatePositions(self):
        if len(self.prices) > 24:
            macd = self.indicator.MACD(self.prices)
            rsi = self.indicator.RSI(self.prices)
            print(macd)
            for tradePairKey, trade in self.trades.items():
                if trade.status == "OPEN":
                    self.closeTrade(macd, trade)
            for v in self.trades:
                if v == self.pair:
                    self.tradeByPair = self.tradeByPair + 1
            if (macd is not None) & (rsi != 0):
                if self.tradeByPair < self.maxTradesPerPair:
                    self.openTrade(macd, rsi)
            self.tradeByPair = 0

    def closeTrade(self, macd, trade):
        if macd == -1:
            tradeProfit = trade.close(self.currentPrice, 0)
            self.strategyPnL += tradeProfit
            self.output.logClose("Strategy running PnL: " + str(self.strategyPnL))
            self.closedPosCounter += 1

    def openTrade(self, macd, rsi):
        if len(self.prices) > 35:
            if macd == 1:
                trade = (BotTrade(self.currentPrice, 0.1,,,,)
                self.trades[self.pair] = trade
                trade.showTrade()


# NOTES
# If underlying prices make a new high or low that isn't
# confirmed by the RSI, this divergence can signal a price reversal.
# If the RSI makes a lower high and then follows with a downside move below
# a previous low, a Top Swing Failure has occurred. If the RSI makes a higher
# low and then follows with an upside move above a previous high, a Bottom
# Swing Failure has occurred.
