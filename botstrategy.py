from botlog import BotLog
from botindicators import BotIndicators
from bottrade import BotTrade

MAXTRADESPERPAIR = 1


class BotStrategy(object):
    def __init__(self):
        self.output = BotLog()
        self.prices = []
        self.closes = []  # Needed for Momentum Indicator
        self.trades = []
        self.currentPrice = ""
        self.currentClose = ""
        self.accumProfit = 0
        self.closedPosCounter = 0

    def tick(self, candlestick):
        self.currentPrice = float(candlestick.priceAverage)
        self.prices.append(self.currentPrice)
        botindicator = BotIndicators()
        # self.currentClose = float(candlestick['close'])
        # self.closes.append(self.currentClose)
        # if self.indicators.movingAverage(self.prices, 15) is not None:
       # self.output.log("Price: " + str(candlestick.priceAverage) + "\tMoving Average: " +
        #                str(botindicator.movingAverage(self.prices, 24) + "\n"))

        self.evaluatePositions()
        self.showPositions()

    def evaluatePositions(self):

        # build for checking multiple pairs on each tick
        openTrades = []

        for trade in self.trades:
            if trade.status == "OPEN":
                openTrades.append(trade)

        if len(openTrades) < MAXTRADESPERPAIR:
            if len(self.prices) > 35:
                indicator = BotIndicators()
                macdVal = indicator.MACD(self.prices)
                if macdVal > 60:
                    self.trades.append(BotTrade(self.currentPrice, stopLossPrice=.001))
        # weight = 0
        # weight += self.checkRSI(self.prices)
        # weight += self.checkMACD(self.prices)
        # weight += self.checkMomentum(self.prices)
        # if weight >= 70:
        #      self.trades.append(BotTrade(self.currentPrice, stopLossPrice=.001))

        # TODO: Refactor Clean up close/stoploss
        for trade in openTrades:
            if self.currentPrice >= (trade.entryPrice * 1.01):
                trade.close(self.currentPrice)
                self.accumProfit += trade.profit
                self.closedPosCounter += 1
                self.output.log(
                    "Strategy Profit/Loss: " + str(self.accumProfit) + "\n" + str(self.closedPosCounter) + "\n")

            # if float(self.currentPrice) > float(self.indicators.movingAverage(self.prices, 15)):
            #	trade.close(self.currentPrice)
            if trade.status == "OPEN":
                trade.stopLoss(self.currentPrice)

    def showPositions(self):
        for trade in self.trades:
            trade.showTrade()

    def checkRSI(self, prices):
       # rsiVal = RSI(prices)
        weightVal = 0
        #if rsiVal > 70 & rsiVal <= 79:
       #     weightVal = 11
        #if rsiVal >= 80 & rsiVal <= 89:
         #   weightVal = 22
        #if rsiVal >= 90 & rsiVal < 100:
         #   weightVal = 33
#        return weightVal
        pass

    def checkMACD(self, prices):
        pass

    def checkMomentum(self, prices):
        pass

# If underlying prices make a new high or low that isn't
# confirmed by the RSI, this divergence can signal a price reversal.
# If the RSI makes a lower high and then follows with a downside move below
# a previous low, a Top Swing Failure has occurred. If the RSI makes a higher
# low and then follows with an upside move above a previous high, a Bottom
# Swing Failure has occurred.
