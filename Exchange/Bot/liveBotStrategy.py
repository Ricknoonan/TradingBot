import csv

from Exchange.Bot.PairPrices import PairPrices
from ScannerBot.BinanceUtil import getClient
from Utils.botlog import BotLog
from Exchange.Bot.bottrade import BotTrade
import pandas as pd
import math
import talib as ta

checkTA = False


def writeCSV(row):
    with open('liveTest.csv', 'a', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(row)


def stopLoss(trade, currentPrice):
    difference = currentPrice - trade.getEntryPrice()
    percentDiff = (difference / currentPrice) * 100
    if percentDiff < -80:
        return True
    else:
        return False


def stopProfit(trade, currentPrice):
    difference = currentPrice - trade.getEntryPrice()
    percentDiff = (difference / currentPrice) * 100
    if percentDiff > 5:
        return True
    else:
        return False


class liveBotStrategy(object):
    def __init__(self, liveFeed):
        self.output = BotLog()
        self.closes = []
        self.trades = {}
        self.maxTradesPerPair = 10
        self.tradeByPair = 0
        self.openTrades = {}
        self.currentClose = ""
        self.accumLiveProfit = 0
        self.closedLivePosCounter = 0
        self.liveFeed = liveFeed
        self.momentumCounter = 0
        self.accumProfit = 0
        self.closedPosCounter = 0
        self.pairPriceDict = {}

    def tick(self, price, pair, currentTimeStamp):
        currentPrice = float(price)
        pairPrices = self.pairPriceDict.get(pair)  # does the dict get updated with the new object ?
        if pairPrices is None:
            pairPrices = PairPrices()
        pairPrices.pricePairList.append(currentPrice)
        self.pairPriceDict[pair] = pairPrices
        return self.evaluatePositions(currentTimeStamp, pair, currentPrice, pairPrices)

    def evaluatePositions(self, currentTimeStamp, pair, currentPrice, pairPrices):
        pairPriceList = pairPrices.pricePairList
        priceSeries = pd.Series(pairPriceList)
        if len(priceSeries) > 24:
            if len(priceSeries) > 35:
                del pairPriceList[
                    0]  # test this logic, does this do the correct deletion and keep the list at 35 per coin once reached?
                pairPrices.isLimitReached = True
            rsi = ta.RSI(priceSeries, 24).iloc[-1]
            macd = ta.MACD(priceSeries)[0].iloc[-1]
            trade = self.trades.get(pair)
            if math.isnan(macd) is False and math.isnan(rsi) is False:
                if trade is not None and trade.status == "OPEN":
                    self.closeTrade(trade, currentTimeStamp, pair, rsi, currentPrice)
                    if trade.isClosed():
                        return trade
                else:
                    self.openTrade(rsi, macd, pair, currentTimeStamp, currentPrice)

    # TODO: remove print and txt file logging so that there is only csv
    def closeTrade(self, trade, currentTimeStamp, pair, rsi, currentPrice):
        if stopLoss(trade, currentPrice) or stopProfit(trade, currentPrice) or (rsi > 75):
            trade.close(currentPrice, currentTimeStamp)
            if self.liveFeed:
                self.accumLiveProfit += trade.profit
                self.closedLivePosCounter += 1
                rows = []
                with open('Trades.csv', 'r') as f:
                    csvReader = csv.reader(f)
                    for row in csvReader:
                        if row[0] == pair and row[5] == 'OPEN':
                            row[5] = 'CLOSED'
                        rows.append(row)
                    # csvWriter = csv.writer(f)
                    # csvWriter.writerows(rows)
            else:
                self.accumProfit += trade.profit
                self.closedPosCounter += 1
                self.output.logCloseTest("Total Profit: " + str(self.accumProfit) + " Trade Profit: " + str(
                    trade.profit) + " Coin pair: " + str(pair))

    # TODO: remove print and txt file logging so that there is only csv
    def openTrade(self, rsi, macd, pair, currentTimeStamp, currentPrice):
        if (35 > rsi > 0) and (self.isOpen(pair)):
            client = getClient()
            btc = pair[-3:]
            btcUSD = btc + "USDT"
            priceUSD = client.get_symbol_ticker(symbol=btcUSD)
            positionSize = 100 / float(priceUSD.get('price'))
            quantity = positionSize / float(currentPrice)
            if self.liveFeed:
                self.trades[pair] = (
                    BotTrade(currentPrice, 0.1, quantity, positionSize, pair, 0, liveTrade=True))
                print("Live Trade Opened for this amount: " + str(positionSize))
                with open('Trades.csv', 'a+', encoding='UTF8') as f:
                    writer = csv.writer(f)
                    writer.writerow([pair, currentPrice, quantity, positionSize, currentTimeStamp, 'OPEN', rsi, macd])
                # client.create_order(symbol=coin, type="MARKET", quantity=amount)
            else:
                self.trades[pair] = (
                    BotTrade(currentPrice, 0.1, quantity, positionSize, pair, 0, liveTrade=False))
                print("Test Trade Opened for this amount: " + str(positionSize))

    def isOpen(self, pair):
        if len(self.trades) > 0:
            for symbol, trade in self.trades.items():
                if (symbol == pair) & (trade.status == "OPEN"):
                    return False
                else:
                    return True
        else:
            return True

    def backFill(self, pair, indicatorBackFill):
        self.pairPriceDict[pair] = indicatorBackFill

    def addExistingTrades(self, btcPairs):
        with open('Trades.csv', 'a+') as f:
            csvReader = csv.reader(f)
            for line in csvReader:
                if len(line) > 0:
                    if line[5] == 'OPEN':
                        btcPairs.append(line[0])
                        self.trades[line[0]] = (
                            BotTrade(float(line[1]), 0.1, float(line[2]), float(line[3]), line[0], 0, liveTrade=True))

        return btcPairs

    def checkPair(self, pair):
        global checkTA
        if checkTA:
            priceList = self.pairPriceDict[pair]
            priceSeries = pd.Series(priceList)
            rsi = ta.RSI(24, priceSeries).iloc[-1]
            return (rsi is None) or (rsi == 0) or math.isnan(rsi)
        else:
            return False


def getExistingPairs(self, smallCapCoins):
    for k, v in self.trades:
        smallCapCoins.append(k)
