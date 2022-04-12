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
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

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


def sortByMarketCap(datum):
    marketCap = {}
    for coin in datum:
        marketCapAmn = coin.get('quote').get('USD').get('market_cap')
        percentChange24h = coin.get('quote').get('USD').get('percent_change_24h')
        percentChange1hr = coin.get('quote').get('USD').get('percent_change_1h')
        if (marketCapAmn > 100000) & (percentChange24h > 5) & (percentChange1hr > 1):
            marketCap[coin.get('symbol')] = marketCapAmn
    sortedDict = {k: v for k, v in sorted(marketCap.items(), key=lambda item: item[1])}
    return sortedDict


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


def compare(baseBTC, marketCapDict):
    quotes = []
    for key, marketCapValue in marketCapDict.items():
        for quote, price in baseBTC.items():
            if (quote == key) & (len(quotes) < 2) & (quote not in quotes):
                quotes.append(quote)
    if len(quotes) > 0:
        return quotes
    else:
        return "No Match"


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


def strategyFeed(smallCapCoins, backTestDays, interval):
    client = getClient()
    strategy = liveBotStrategy(liveFeed=True)
    smallCapCoins = backTestFeed(smallCapCoins, backTestDays, interval, liveBotStrategy)
    nextCoins = []
    intervalInMiliSeconds = getMiliSeconds(interval)
    print(smallCapCoins)
    while True:
        if len(smallCapCoins) == 0:
            break
        for coin in smallCapCoins:
            try:
                currentPriceDict = client.get_symbol_ticker(symbol=coin)
            except ConnectionError:
                sleep(60)
                print("Retrying connection for: " + coin)
                currentPriceDict = client.get_symbol_ticker(symbol=coin)
            currentPrice = currentPriceDict.get('price')
            currentTS = getCurrentTS()
            trade = strategy.tick(currentPrice, coin, currentTS)
            print(coin + "\n" + currentPrice)
            if trade is not None:
                if trade.status == 'CLOSED':
                    if trade.getProfit() > 0:
                        nextCoins.append(coin)
                    smallCapCoins.remove(coin)
        sleep(intervalInMiliSeconds)
    print("Finished looping through " + str(smallCapCoins) + ". Sleeping for: " + str(intervalInMiliSeconds))
    sleep(intervalInMiliSeconds)
    return nextCoins


def getHistoricalStart(days):
    historicalDate = date.today() - timedelta(days)
    dt = datetime.combine(historicalDate, datetime.min.time())
    ts = datetime.timestamp(dt)
    return ts.__int__()


# def volatilityIndex():


def backTestFeed(smallCapCoins, backTestDays, interval, liveStrategy):
    client = getClient()
    nextCoin = False
    newCoinList = []
    backTestStartTS = getHistoricalStart(backTestDays)
    for pair in smallCapCoins:
        coinDict = {}
        strategy = BotStrategy3(pair, liveFeed=False)
        historicalOutput = client.get_historical_klines(symbol=pair, interval=interval, start_str=backTestStartTS)
        counter = 0
        for kline in historicalOutput:
            if counter < 1000:
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
                counter += 1
        # priceFrame = pd.DataFrame(historicalOutput)
        # priceFrame['returns'] = (np.log(priceFrame.close /
        #                                 priceFrame.close.shift(-1)))
        # volIndex = strategy.getVolIndex()
        if coinDict.get(pair) is not None and ((coinDict.get(pair)) > 0):
            newCoinList.append(pair)
        nextCoin = True
    return newCoinList


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


def Main():
    backTestDays = 10
    interval = "15m"
    smallCapCoins = []
    while True:
        baseBTC = binanceData()
        marketCapDict = marketCapData()
        newList = compare(baseBTC, marketCapDict)
        smallCapCoins = addToList(newList, smallCapCoins)
        print(smallCapCoins)
        if smallCapCoins != "No Match":
            smallCapCoins = toBTC(smallCapCoins)
            nextCoins = strategyFeed(smallCapCoins, backTestDays, interval)
            smallCapCoins = nextCoins
            sleep(10)
        else:
            sleep(1800)


if __name__ == "__main__":
    Main()
