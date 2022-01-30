from ScannerBot.BinanceUtil import getClient
from Utils.botlog import BotLog
from Exchange.Bot.botindicators import BotIndicators
from Exchange.Bot.bottrade import BotTrade
import pandas as pd


class BotStrategy3(object):
    def __init__(self, pair, liveFeed):
        self.output = BotLog()
        self.prices = []
        self.closes = []
        self.trades = {}
        self.maxTradesPerPair = 10
        self.tradeByPair = 0
        self.openTrades = {}
        self.currentPrice = ""
        self.currentClose = ""
        self.accumLiveProfit = 0
        self.closedLivePosCounter = 0
        self.indicator = BotIndicators(long_prd=26, short_prd=12, signal_long_length=9, )
        self.pair = pair
        self.liveFeed= liveFeed
        self.momentumCounter = 0
        self.accumProfit = 0
        self.closedPosCounter = 0


    def tick(self, price, nextCoin, currentTimeStamp):
        self.currentPrice = float(price)
        if nextCoin:
            self.prices = []
        else:
            self.prices.append(self.currentPrice * 1000)
        return self.evaluatePositions(currentTimeStamp)

    def evaluatePositions(self, currentTimeStamp):
        priceFrame = pd.DataFrame({'price': self.prices})
        print("Number of prices: " + str(len(priceFrame)))
        if len(priceFrame) > 24:
            momentum = self.indicator.momentumROC(self.prices)
            rsi = self.indicator.RSI(priceFrame)
            macd = self.indicator.MACD(priceFrame)
            for tradePairKey, trade in self.trades.items():
                if trade.status == "OPEN":
                    self.closeTrade(trade, currentTimeStamp)
                    if trade.isClosed():
                        return trade
            if momentum > 100:
                self.momentumCounter += 1
            if momentum < 100:
                self.momentumCounter = 0
            self.openTrade(rsi, macd)

    def closeTrade(self, trade, currentTimeStamp):
        if self.stopLoss(trade) or self.stopProfit(trade):
            trade.close(self.currentPrice, currentTimeStamp)
            if self.liveFeed:
                self.accumLiveProfit += trade.profit
                self.closedLivePosCounter += 1
                self.output.logClose("Profit: " + str(self.accumLiveProfit))
                print("Closed trade at this iteration" + str(len(self.prices)) + "This many trades have closed")
            else:
                self.accumProfit += trade.profit
                self.closedPosCounter += 1
                self.output.logClose("Profit: " + str(self.accumProfit))

    # TODO: Find way of getting price quoted in a fiat currency
    def openTrade(self, rsi, macd):
        if ((40 > rsi > 0) or (macd == 1)) and (self.isOpen()):
            client = getClient()
            btc = self.pair[-3:]
            btcUSD = btc + "USDT"
            priceUSD = client.get_symbol_ticker(symbol=btcUSD)
            positionSize = 100 / float(priceUSD.get('price'))
            quantity = positionSize / float(self.currentPrice)
            if self.liveFeed:
                self.trades[self.pair] = (
                    BotTrade(self.currentPrice, 0.1, quantity, positionSize, self.pair, 0, liveTrade=True))
                print("Live Trade Opened for this amount: " + str(positionSize))
                # client.create_order(symbol=self.pair, type="MARKET", quantity=amount)
                self.output.logOpen("Live Trade opened")
            else:
                self.trades[self.pair] = (
                    BotTrade(self.currentPrice, 0.1, quantity, positionSize, self.pair, 0, liveTrade=False))
                print("Test Trade Opened for this amount: " + str(positionSize))
                # client.create_order(symbol=self.pair, type="MARKET", quantity=amount)
                self.output.logOpen("Test Trade opened")

    def isOpen(self):
        if len(self.trades) > 0:
            for symbol, trade in self.trades.items():
                if (symbol == self.pair) & (trade.status == "OPEN"):
                    return False
                else:
                    return True
        else:
            return True

    def stopLoss(self, trade):
        difference = self.currentPrice - trade.getEntryPrice()
        print("Diff: " + str(difference))
        percentDiff = (difference / self.currentPrice) * 100
        if percentDiff < -75:
            return True
        else:
            return False

    def stopProfit(self, trade):
        difference = self.currentPrice - trade.getEntryPrice()
        percentDiff = (difference / self.currentPrice) * 100
        if percentDiff > 10:
            return True
        else:
            return False
