from Exchange.Bot.botlog import BotLog
from Exchange.Bot.botindicators import BotIndicators
from Exchange.Bot.bottrade import BotTrade


class BotStrategy(object):
    def __init__(self, pair):
        self.output = BotLog()
        self.prices = []
        self.closes = []  # Needed for Momentum Indicator
        self.trades = []
        self.maxTradesPerPair = 1
        self.tradeByPair = 0
        self.openTrades = {}
        self.currentPrice = ""
        self.currentClose = ""
        self.accumProfit = 0
        self.closedPosCounter = 0
        self.indicator = BotIndicators(long_prd=26, short_prd=12, signal_long_length=9, )
        self.pair = pair

    def tick(self, candlestick):
        self.currentPrice = float(candlestick.priceAverage)
        self.prices.append(self.currentPrice)
        self.evaluatePositions()
        self.showPositions()

    def evaluatePositions(self):
        macd = 0
        rsi = 0
        for trade in self.trades:
            if trade.status == "OPEN":
                self.openTrades[self.pair] = trade
        if len(self.prices) > 24:
            macd = self.indicator.MACD(self.prices)
            rsi = self.indicator.RSI(self.prices)
        for v in self.openTrades:
            if v == self.pair:
                self.tradeByPair = self.tradeByPair + 1

        if (macd != 0) & (rsi != 0):
            self.openTrade(macd, rsi)
        if len(self.openTrades) > 0:
            self.closeTrade(self.openTrades, macd, rsi)

    def showPositions(self):
        for trade in self.trades:
            trade.showTrade()

    def closeTrade(self, openTrades, macd, rsi):
        for tradePairKey, trade in openTrades.items():
            if (macd == -1) & (rsi < 30):
                trade.close(self.currentPrice)
                self.accumProfit += trade.profit
                self.closedPosCounter += 1
                self.output.log(
                    "Strategy Profit/Loss: " + str(self.accumProfit) + "\n" + str(self.closedPosCounter) + "\n")
            if trade.status == "OPEN":
                trade.stopLoss(self.currentPrice)

    def openTrade(self, macd, rsi):
        if self.tradeByPair < self.maxTradesPerPair:
            if len(self.prices) > 35:
                self.output.log("Price: macdVal =" + str(macd))
                self.output.log("Price: rsi =" + str(rsi))
                if (macd == 1) & (rsi < 70):
                    self.trades.append(BotTrade(self.currentPrice, 0.1))

# NOTES
# If underlying prices make a new high or low that isn't
# confirmed by the RSI, this divergence can signal a price reversal.
# If the RSI makes a lower high and then follows with a downside move below
# a previous low, a Top Swing Failure has occurred. If the RSI makes a higher
# low and then follows with an upside move above a previous high, a Bottom
# Swing Failure has occurred.
