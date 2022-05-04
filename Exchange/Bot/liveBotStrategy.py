import csv

from ScannerBot.BinanceUtil import getClient
from Utils.botlog import BotLog
from Exchange.Bot.botindicators import BotIndicators
from Exchange.Bot.bottrade import BotTrade
import pandas as pd
import math
import talib as ta

checkTA = False


def writeCSV(row):
    with open('liveTest.csv', 'a', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(row)


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
        prices.append(self.currentPrice)
        self.coinPriceDict[pair] = prices
        return self.evaluatePositions(currentTimeStamp, pair)

    def evaluatePositions(self, currentTimeStamp, pair):
        pricePairList = self.coinPriceDict[pair]
        priceSeries = pd.Series(pricePairList)
        if len(priceSeries) > 24:
            if len(priceSeries) > 35:
                del pricePairList[0]
                global checkTA
                checkTA = True
            rsi = ta.RSI(priceSeries, 24).iloc[-1]
            macd = ta.MACD(priceSeries)[0].iloc[-1]
            writeCSV([str(currentTimeStamp), str(pair), str(self.currentPrice), str(macd), str(rsi)])
            trade = self.trades.get(pair)
            if math.isnan(macd) is False and math.isnan(rsi) is False:
                if trade is not None and trade.status == "OPEN":
                    self.closeTrade(trade, currentTimeStamp, pair, macd, rsi)
                    if trade.isClosed():
                        return trade
                else:
                    self.openTrade(rsi, macd, pair, currentTimeStamp)

    def closeTrade(self, trade, currentTimeStamp, pair, macd, rsi):
        if self.stopLoss(trade) or self.stopProfit(trade) or (rsi > 75):
            trade.close(self.currentPrice, currentTimeStamp)
            if self.liveFeed:
                self.accumLiveProfit += trade.profit
                self.closedLivePosCounter += 1
                self.output.logCloseLive("Total Profit: " + str(self.accumProfit) + " Trade Profit: " + str(
                    trade.profit) + " Coin pair: " + str(pair))
                with open('Trades.csv', 'w', encoding='UTF8') as f:
                    readerObj = csv.reader(f)
                    writer = csv.writer(f)
                    for line in readerObj:
                        if line[0] == pair & line[5] == 'OPEN':
                            line[5] = 'CLOSED'
                            writer.writerows(readerObj)
            else:
                self.accumProfit += trade.profit
                self.closedPosCounter += 1
                self.output.logCloseTest("Total Profit: " + str(self.accumProfit) + " Trade Profit: " + str(
                    trade.profit) + " Coin pair: " + str(pair))

    def openTrade(self, rsi, macd, pair, currentTimeStamp):
        if (35 > rsi > 0) and (self.isOpen(pair)):
            client = getClient()
            btc = pair[-3:]
            btcUSD = btc + "USDT"
            priceUSD = client.get_symbol_ticker(symbol=btcUSD)
            positionSize = 100 / float(priceUSD.get('price'))
            quantity = positionSize / float(self.currentPrice)
            if self.liveFeed:
                self.trades[pair] = (
                    BotTrade(self.currentPrice, 0.1, quantity, positionSize, pair, 0, liveTrade=True))
                print("Live Trade Opened for this amount: " + str(positionSize))
                with open('Trades.csv', 'a', encoding='UTF8') as f:
                    writer = csv.writer(f)
                    writer.writerow([pair, self.currentPrice, quantity, positionSize, currentTimeStamp, 'OPEN'])
                # client.create_order(symbol=coin, type="MARKET", quantity=amount)
                self.output.logOpenLive(
                    str(currentTimeStamp) + " " + str(pair) + " RSI: " + str(rsi) + " MACD: " + str(macd))
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

    def addExistingTrades(self, smallCapCoins):
        with open('Trades.csv') as f:
            readerObj = csv.reader(f)
            for line in readerObj:
                if line[5] == 'OPEN':
                    smallCapCoins.append(line[0])
                    self.trades[line[0]] = (
                        BotTrade(line[1], 0.1, line[2], line[3], line[0], 0, liveTrade=True))
        return smallCapCoins

    def getExistingPairs(self, smallCapCoins):
        for k, v in self.trades:
            smallCapCoins.append(k)

    def checkPair(self, pair):
        global checkTA
        if checkTA:
            priceList = self.coinPriceDict[pair]
            priceSeries = pd.Series(priceList)
            rsi = ta.RSI(24, priceSeries).iloc[-1]
            if (rsi is None) or (rsi == 0):
                return True
