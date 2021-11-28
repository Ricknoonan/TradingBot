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
            print("This is RSI: " + str(rsi) + "and this is MACD: " + str(macd))
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
            self.accumProfit += trade.profit
            self.closedPosCounter += 1
            self.output.logClose("Profit: " + str(self.accumProfit))
            print("Closed trade at this iteration" + str(len(self.prices)) + "This many trades have closed")

    # TODO: Find way of getting price quoted in a fiat currency
    def openTrade(self, rsi, macd):
        if ((40 > rsi > 0) or (macd == 1)) and (self.isOpen()):
            client = getClient()
            btc = self.pair[-3:]
            btcUSD = btc + "USDT"
            priceUSD = client.get_symbol_ticker(symbol=btcUSD)
            positionSize = 100 / float(priceUSD.get('price'))
            quantity = positionSize / float(self.currentPrice)
            self.trades[self.pair] = (BotTrade(self.currentPrice, 0.1, quantity, positionSize, self.pair, 0))
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
        if percentDiff > 20:
            return True
        else:
            return False
