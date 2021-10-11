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

    def tick(self, price):
        self.currentPrice = float(price)
        self.prices.append(self.currentPrice)
        self.evaluatePositions()

    def evaluatePositions(self):
        priceFrame = pd.DataFrame({'price': self.prices})
        if len(priceFrame) > 24:
            momentum = self.indicator.momentumROC(self.prices)
            rsi = self.indicator.RSI(priceFrame) > 60
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

    def closeTrade(self, rsi, trade):
        if rsi > 60:
            trade.close(self.currentPrice)
            self.accumProfit += trade.profit
            self.closedPosCounter += 1

    def openTrade(self, rsi):
        if self.momentumCounter > 5 & (rsi < 40):
            self.trades[self.pair] = (BotTrade(self.currentPrice, 0.1))
            client = getClient()
            base = self.pair[3]
            base = base + "USD"
            priceUSD = client.get_symbol_ticker(base)
            amount = 10 / priceUSD
            client.create_order(symbol=self.pair, type="MARKET", quantity=amount)
