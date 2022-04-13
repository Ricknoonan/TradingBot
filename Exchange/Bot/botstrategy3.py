from ScannerBot.BinanceUtil import getClient
from Utils.botlog import BotLog
from Exchange.Bot.botindicators import BotIndicators
from Exchange.Bot.bottrade import BotTrade
import pandas as pd
import talib as ta
import math
import csv


def writeCSV(row):
    with open('backtest.csv', 'a', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(row)

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
        self.liveFeed = liveFeed
        self.momentumCounter = 0
        self.accumProfit = 0
        self.closedPosCounter = 0

    def tick(self, price, nextCoin, currentTimeStamp):
        self.currentPrice = float(price)
        if nextCoin:
            self.prices = []
        else:
            self.prices.append(self.currentPrice)
        return self.evaluatePositions(currentTimeStamp)

    def evaluatePositions(self, currentTimeStamp):
        priceSeries = pd.Series(self.prices)
        priceFrame = pd.DataFrame({'price': self.prices})
        if len(priceFrame) > 27:
            rsi = ta.RSI(priceSeries, 24).iloc[-1]
            macd = ta.MACD(priceSeries)[0].iloc[-1]
            writeCSV([str(self.pair), str(self.currentPrice), str(macd), str(rsi)])
            if math.isnan(macd) is False and math.isnan(rsi) is False:
                for tradePairKey, trade in self.trades.items():
                    if trade.status == "OPEN":
                        self.closeTrade(trade, currentTimeStamp, macd, rsi)
                        if trade.isClosed():
                            return trade
                self.openTrade(rsi, macd, currentTimeStamp)

    def closeTrade(self, trade, currentTimeStamp, macd, rsi):
        if self.stopLoss(trade) or self.stopProfit(trade) or (rsi > 70):
            trade.close(self.currentPrice, currentTimeStamp)
            if self.liveFeed:
                self.accumLiveProfit += trade.profit
                self.closedLivePosCounter += 1
                self.output.logCloseLive("Profit: " + str(self.accumLiveProfit))
            else:
                self.accumProfit += trade.profit
                self.closedPosCounter += 1
                self.output.logCloseTest("Total Profit: " + str(self.accumProfit) + " Trade Profit: " + str(
                    trade.profit) + " Coin pair: " + str(self.pair))

    def openTrade(self, rsi, macd, currentTimestamp):
        if (30 > rsi > 0) and (self.isOpen()):
            client = getClient()
            btc = self.pair[-3:]
            btcUSD = btc + "USDT"
            priceUSD = client.get_symbol_ticker(symbol=btcUSD)
            positionSize = 10 / float(priceUSD.get('price'))
            quantity = positionSize / float(self.currentPrice)
            if self.liveFeed:
                self.trades[self.pair] = (
                    BotTrade(self.currentPrice, 0.1, quantity, positionSize, self.pair, currentTimestamp, liveTrade=True))
                print("Live Trade Opened for this amount: " + str(positionSize))
                # client.create_order(symbol=self.pair, type="MARKET", quantity=amount)
                self.output.logOpenLive("Live Trade opened")
            else:
                self.trades[self.pair] = (
                    BotTrade(self.currentPrice, 0.1, quantity, positionSize, self.pair, currentTimestamp, liveTrade=False))
                print("Test Trade Opened for this amount: " + str(positionSize))
                self.output.logOpenTest("Test Trade opened")

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
        percentDiff = (difference / self.currentPrice) * 100
        if percentDiff < -80:
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
#TODO: getVolindex to work with https://tinytrader.io/how-to-calculate-historical-price-volatility-with-python/
    def getVolIndex(self):
        volIndex = 0
        return volIndex
