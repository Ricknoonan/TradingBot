from ScannerBot.BinanceUtil import getClient
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
        self.momentumCounter = 0

    def tick(self, price, nextCoin):
        self.currentPrice = float(price)
        if nextCoin:
            self.prices = []
        else:
            self.prices.append(self.currentPrice * 1000)
        return self.evaluatePositions()

    def evaluatePositions(self):
        priceFrame = pd.DataFrame({'price': self.prices})
        print("Number of prices: " + str(len(priceFrame)))
        if len(priceFrame) > 24:
            momentum = self.indicator.momentumROC(self.prices)
            rsi = self.indicator.RSI(priceFrame)
            print("This is RSI: " + str(rsi) + "and this is momentum: " + str(momentum))
            for tradePairKey, trade in self.trades.items():
                if trade.status == "OPEN":
                    self.closeTrade(momentum, trade)
                    if trade.isClosed():
                        return trade
            if momentum > 100:
                self.momentumCounter += 1
            if momentum < 100:
                self.momentumCounter = 0
            self.openTrade(rsi)

    # or (self.momentumCounter < -3)
    def closeTrade(self, rsi, trade):
        if (rsi > 65) & (rsi < 100):
            trade.close(self.currentPrice)
            self.accumProfit += trade.profit
            self.closedPosCounter += 1
            self.output.logClose("Profit: " + str(self.accumProfit))
            print("Closed trade at this iteration" + str(len(self.prices)) + "This many trades have closed")

 #   (self.momentumCounter > 3) or
    # TODO: Find way of getting price quoted in a fiat currency
    def openTrade(self, rsi):
        if (40 > rsi > 0) and (self.isOpen()):
            client = getClient()
            btc = self.pair[-3:]
            btcUSD = btc + "USDT"
            priceUSD = client.get_symbol_ticker(symbol=btcUSD)
            positionSize = 10 / float(priceUSD.get('price'))
            quantity = float(self.currentPrice) / positionSize
            self.trades[self.pair] = (BotTrade(self.currentPrice, 0.1, quantity, positionSize))
            print("Trade Opened for this amount: " + str(positionSize))
            # client.create_order(symbol=self.pair, type="MARKET", quantity=amount)
            self.output.logOpen("Trade opened")

    def isOpen(self):
        if len(self.trades) > 0:
            for symbol, trade in self.trades.items():
                if (symbol == self.pair) & (trade.status == "OPEN"):
                    return False
                else:
                    return True
        else:
            return True
