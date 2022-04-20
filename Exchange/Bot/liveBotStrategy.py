
from ScannerBot.BinanceUtil import getClient
from Utils.botlog import BotLog
from Exchange.Bot.botindicators import BotIndicators
from Exchange.Bot.bottrade import BotTrade
import pandas as pd
import math
import talib as ta

class liveBotStrategy(object):
    def __init__(self, liveFeed):
        self.output = BotLog()
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
        self.liveFeed = liveFeed
        self.momentumCounter = 0
        self.accumProfit = 0
        self.closedPosCounter = 0
        self.coinPriceDict = {}

    def tick(self, price, pair, currentTimeStamp):
        self.currentPrice = float(price)
        prices = self.coinPriceDict.get(pair)
        if prices is None:
            prices = []
            while len(prices) < 20:
                prices.append(self.currentPrice)
            self.coinPriceDict[pair] = prices
        else:
            prices.append(self.currentPrice)
            self.coinPriceDict[pair] = prices
        return self.evaluatePositions(currentTimeStamp, pair)

    def evaluatePositions(self, currentTimeStamp, pair):
        priceSeries = pd.Series(self.coinPriceDict[pair])
        if len(priceSeries) > 26:
            rsi = ta.RSI(priceSeries, 24).iloc[-1]
            macd = ta.MACD(priceSeries)[0].iloc[-1]
            trade = self.trades.get(pair)
            if math.isnan(macd) is False and math.isnan(rsi) is False:
                if trade is not None and trade.status == "OPEN":
                    self.closeTrade(trade, currentTimeStamp, pair, macd, rsi)
                    if trade.isClosed():
                        return trade
                else:
                    self.openTrade(rsi, macd, pair)

    def closeTrade(self, trade, currentTimeStamp, pair, macd, rsi):
        if self.stopLoss(trade) or self.stopProfit(trade) or (rsi > 75):
            trade.close(self.currentPrice, currentTimeStamp)
            if self.liveFeed:
                self.accumLiveProfit += trade.profit
                self.closedLivePosCounter += 1
                self.output.logCloseLive("Profit: " + str(self.accumLiveProfit))
            else:
                self.accumProfit += trade.profit
                self.closedPosCounter += 1
                self.output.logCloseTest("Total Profit: " + str(self.accumProfit) + " Trade Profit: " + str(
                    trade.profit) + " Coin pair: " + str(pair))

    def openTrade(self, rsi, macd, pair):
        if (35 > rsi > 0) and (self.isOpen(pair)):
            client = getClient()
            btc = pair[-3:]
            btcUSD = btc + "USDT"
            priceUSD = client.get_symbol_ticker(symbol=btcUSD)
            positionSize = 10 / float(priceUSD.get('price'))
            quantity = positionSize / float(self.currentPrice)
            if self.liveFeed:
                self.trades[pair] = (
                    BotTrade(self.currentPrice, 0.1, quantity, positionSize, pair, 0, liveTrade=True))
                print("Live Trade Opened for this amount: " + str(positionSize))
                # client.create_order(symbol=coin, type="MARKET", quantity=amount)
                self.output.logOpenLive("Live Trade opened")
            else:
                self.trades[pair] = (
                    BotTrade(self.currentPrice, 0.1, quantity, positionSize, pair, 0, liveTrade=False))
                print("Test Trade Opened for this amount: " + str(positionSize))
                self.output.logOpenTest("Test Trade opened")

    def isOpen(self, pair):
        if len(self.trades) > 0:
            for symbol, trade in self.trades.items():
                if (symbol == pair) & (trade.status == "OPEN"):
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
        if percentDiff > 5:
            return True
        else:
            return False

    def backFill(self, pair, indicatorBackFill):
        self.coinPriceDict[pair] = indicatorBackFill




