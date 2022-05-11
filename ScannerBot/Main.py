import operator
from time import sleep
import calendar
import json
import time
from datetime import date, timedelta
from datetime import datetime
from time import sleep
import pandas as pd
# import talib
import numpy as np

from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects, ReadTimeout

# binance
# 0 get markets from binance -> Done
# 1. Get small cap coins -> Done
# 1.1. need to get list of all coins traded and sort by market cap. then pick the smallest 10 caps that have a BTC market on binance
# 2. Check for momentum, developer activity, news?
# 2.1. this will involve pulling candlesticks for each small cap coin and running various analysis.
# 3. Buy and sell short term, or buy and hold.
# 3.1.
from Exchange.Bot.botstrategy3 import BotStrategy3
from Exchange.Bot.liveBotStrategy import liveBotStrategy
from ScannerBot.BinanceUtil import getClient

# gmt stores current gmtime
from ScannerBot.TAUtil import runTA


def sortByMarketCap(datum):
    marketCap = {}
    percentChange = {}
    for coin in datum:
        marketCapAmn = coin.get('quote').get('USD').get('market_cap')
        percentChange24h = coin.get('quote').get('USD').get('percent_change_24h')
        percentChange1hr = coin.get('quote').get('USD').get('percent_change_1h')
        percentChange7d = coin.get('quote').get('USD').get('percent_change_7d')
        if (marketCapAmn > 1000000) & ((percentChange24h > 5) and (percentChange7d > 4)):
            marketCap[coin.get('symbol')] = marketCapAmn
            percentChange[coin.get('symbol')] = percentChange24h
    sortedMarketCap = {k: v for k, v in sorted(marketCap.items(), key=lambda item: item[1])}
    sortedPercentChange = dict(sorted(percentChange.items(), key=operator.itemgetter(1), reverse=True))
    return sortedPercentChange


def marketCapData():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '5000',
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'f3f497ea-cba3-4866-80c8-16e0f8e0d02d',
    }
    session = Session()
    session.headers.update(headers)
    datum = None
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        datum = data.get('data')
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    return sortByMarketCap(datum)


def binanceData():
    baseBTC = {}
    client = getClient()
    info = client.get_all_tickers()
    for coin in info:
        if 'BTC' in coin.get('symbol')[-3:]:
            market = coin.get('symbol')
            price = coin.get('price')
            base = market[:-3]
            baseBTC[base] = price
    return baseBTC


def compare(baseBTC, marketCapDict, limit):
    quotes = []
    for key, marketCapValue in marketCapDict.items():
        for quote, price in baseBTC.items():
            if (quote == key) and (len(quotes) < limit) and (quote not in quotes):
                quotes.append(quote)
    return quotes


def getDiff(value, price):
    if value > price:
        percentDiff = (price / value) * 100
    elif price > value:
        percentDiff = (value / price) * 100
    else:
        percentDiff = 0
    return percentDiff


def getCurrentTS():
    gmt = time.gmtime()
    ts = calendar.timegm(gmt)
    return ts


def getMiliSeconds(interval):
    minutes = interval[:-1]
    return int(minutes) * 60


def backTestFeed(smallCapCoins, backTestDays, interval, liveStrategy):
    client = getClient()
    nextCoin = False
    newCoinList = []
    backTestStartTS = getHistoricalStart(backTestDays)
    for pair in smallCapCoins:
        coinDict = {}
        strategy = BotStrategy3(pair, liveFeed=False)
        historicalOutput = client.get_historical_klines(symbol=pair, interval=interval, start_str=backTestStartTS)
        mostRecentKLines = historicalOutput[-2500:]
        for kline in mostRecentKLines:
            currentPrice = kline[4]
            timestamp = kline[0]
            trade = strategy.tick(currentPrice, nextCoin, timestamp)
            nextCoin = False
            print(pair + "\n" + currentPrice)
            if trade is not None:
                if trade.status == 'CLOSED':
                    if coinDict.get(pair) is None:
                        coinDict[pair] = trade.getProfit()
                    else:
                        profit = coinDict.get(pair)
                        coinDict[pair] = trade.getProfit() + profit
        if coinDict.get(pair) is not None and ((coinDict.get(pair)) > 0):
            newCoinList.append(pair)
        nextCoin = True
    return newCoinList


def strategyFeed(btcPairs, interval):
    client = getClient()
    strategy = liveBotStrategy(liveFeed=True)
    btcPairs = strategy.addExistingTrades(btcPairs)  # adds existing open positions on program restart
    intervalInMiliSeconds = getMiliSeconds(interval)
    print(btcPairs)
    counter = 0
    testPrices = [4.57e-06, 4.57e-06, 4.57e-06, 4.58e-06, 4.56e-06, 4.56e-06, 4.53e-06, 4.51e-06, 4.56e-06, 4.55e-06, 4.51e-06, 4.36e-06, 4.35e-06, 4.41e-06, 4.32e-06, 4.28e-06, 4.3e-06, 4.28e-06, 4.3e-06, 4.27e-06, 4.27e-06, 4.27e-06, 4.29e-06, 4.28e-06, 4.26e-06, 4.27e-06, 4.28e-06, 4.28e-06, 4.27e-06, 4.27e-06, 4.25e-06, 4.25e-06, 4.24e-06, 4.23e-06, 4.26e-06, 4.57e-06, 4.57e-06, 4.57e-06, 4.58e-06, 4.56e-06, 4.56e-06, 4.53e-06, 4.51e-06, 4.56e-06, 4.55e-06, 4.51e-06, 4.36e-06, 4.35e-06, 4.41e-06, 4.32e-06, 4.28e-06, 4.3e-06, 4.28e-06, 4.3e-06, 4.27e-06, 4.27e-06, 4.27e-06, 4.29e-06, 4.28e-06, 4.26e-06, 4.27e-06, 4.28e-06, 4.28e-06, 4.27e-06, 4.27e-06, 4.25e-06, 4.25e-06, 4.24e-06, 4.23e-06, 4.26e-06,4.57e-06, 4.57e-06, 4.57e-06, 4.58e-06, 4.56e-06, 4.56e-06, 4.53e-06, 4.51e-06, 4.56e-06, 4.55e-06, 4.51e-06, 4.36e-06, 4.35e-06, 4.41e-06, 4.32e-06, 4.28e-06, 4.3e-06, 4.28e-06, 4.3e-06, 4.27e-06, 4.27e-06, 4.27e-06, 4.29e-06, 4.28e-06, 4.26e-06, 4.27e-06, 4.28e-06, 4.28e-06, 4.27e-06, 4.27e-06, 4.25e-06, 4.25e-06, 4.24e-06, 4.23e-06, 4.26e-06]
    while counter < len(testPrices):
        for pair in btcPairs:
            try:
                currentPriceDict = client.get_symbol_ticker(symbol=pair)
            except (ConnectionError, ReadTimeout):
                sleep(60)
                print("Retrying connection for: " + pair)
                currentPriceDict = client.get_symbol_ticker(symbol=pair)
            # currentPrice = currentPriceDict.get('price')
            currentPrice = testPrices[counter]
            currentTS = getCurrentTS()
            trade = strategy.tick(currentPrice, pair, currentTS)
            if (trade is not None and trade.status == 'CLOSED') or strategy.checkPair(
                    pair):  # if trade is closed out or market is not active, remove it from list so that newer pair can be added
                btcPairs.remove(pair)
                btcPairs.append(getBTCSPairs(1))
        counter += 1
        # sleep(intervalInMiliSeconds)


def getHistoricalStart(days):
    historicalDate = date.today() - timedelta(days)
    dt = datetime.combine(historicalDate, datetime.min.time())
    ts = datetime.timestamp(dt)
    return ts.__int__()


def addToList(newList, smallCapCoins):
    for coin in newList:
        smallCapCoins.append(coin)
    return smallCapCoins


def toBTC(smallCapCoins):
    newList = []
    for smallCapCoin in smallCapCoins:
        smallCapCoin = smallCapCoin + "BTC"
        newList.append(smallCapCoin)
    return newList


def getBTCSPairs(limit):
    baseBTC = binanceData()  # fetch all btc markets
    marketCapDict = marketCapData()  # fetch all tokens listed on CMC.
    symbols = compare(baseBTC, marketCapDict, limit)  # compare these lists
    return toBTC(symbols)


def Main():
    interval = "2m"
    btcPairs = getBTCSPairs(10)
    strategyFeed(btcPairs, interval)


if __name__ == "__main__":
    Main()
