from Exchange.Bot.botlog import BotLog
from Exchange.Bot.botindicators import BotIndicators
from Exchange.Bot.bottrade import BotTrade

MAXTRADESPERPAIR = 1


class BotStrategy(object):
    def __init__(self, pair):
        self.output = BotLog()
        self.prices = []
        self.closes = []  # Needed for Momentum Indicator
        self.trades = []
        self.currentPrice = ""
        self.currentClose = ""
        self.accumProfit = 0
        self.closedPosCounter = 0
        self.indicator = BotIndicators(long_prd=26, short_prd=12, signal_long_length=9, )
        self.pair = pair
#    def __init__(self, long_prd, short_prd, signal_long_length, signal_short_length = 0, column = "Open"):

    def tick(self, candlestick):
        self.currentPrice = float(candlestick.priceAverage)
        self.prices.append(self.currentPrice)
        self.evaluatePositions()
        self.showPositions()

    def evaluatePositions(self):
        #dict key -> value
        #key: pair string "BTCXMR"
        #value: trade object
        openTrades = {}
        tradesByPair = 0
        for trade in self.trades:
            if trade.status == "OPEN":
                openTrades[self.pair] = trade
        macd = self.indicator.MACD(self.prices)
        rsi = self.indicator.RSI(self.prices)
        for v in openTrades:
            if v == self.pair:
                tradesByPair = tradesByPair + 1

        if tradesByPair < MAXTRADESPERPAIR:
            if len(self.prices) > 35:
                self.output.log("Price: macdVal =" + str(macd))
                self.output.log("Price: rsi =" + str(rsi))
                if macd == 1 & rsi < 70:
                    self.trades.append(BotTrade(self.currentPrice, 0.1))

        # TODO: Refactor Clean up close/stoploss
        for trade in openTrades:
            if macd == -1 & rsi < 30:
                trade.close(self.currentPrice)
                self.accumProfit += trade.profit
                self.closedPosCounter += 1
                self.output.log(
                    "Strategy Profit/Loss: " + str(self.accumProfit) + "\n" + str(self.closedPosCounter) + "\n")
            if trade.status == "OPEN":
                trade.stopLoss(self.currentPrice)

    def showPositions(self):
        for trade in self.trades:
            trade.showTrade()

    def checkRSI(self, prices):
        # rsiVal = RSI(prices)
        weightVal = 0
        # if rsiVal > 70 & rsiVal <= 79:
        #     weightVal = 11
        # if rsiVal >= 80 & rsiVal <= 89:
        #   weightVal = 22
        # if rsiVal >= 90 & rsiVal < 100:
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
