import sys
import time

from urllib.error import URLError
import os
from time import sleep
from pythonic_binance.client import Client
from datetime import date, timedelta

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from Utils.botlog import BotLog

import calendar
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

# gmt stores current gmtime

# binance
# 0 get markets from binance -> Done
# 1. Get small cap coins -> Done
# 1.1. need to get list of all coins traded and sort by market cap. then pick the smallest 10 caps that have a BTC market on binance
# 2. Check for momentum, developer activity, news?
# 2.1. this will involve pulling candlesticks for each small cap coin and running various analysis.
# 3. Buy and sell short term, or buy and hold.
# 3.1.
from Exchange.Bot.botcandlestick import BotCandlestick
from Exchange.Bot.botchart import BotChart
from Exchange.Bot.botstrategy import BotStrategy
from Exchange.Bot.botstrategy1 import BotStrategy1
from Exchange.Bot.botstrategy3 import BotStrategy3
from ScannerBot import binanceCredential
from ScannerBot.BinanceUtil import getClient


def sortByMarketCap(datum):
    marketCap = {}
    for coin in datum:
        marketCapAmn = coin.get('quote').get('USD').get('market_cap')
        percentChange24h = coin.get('quote').get('USD').get('percent_change_24h')
        if (marketCapAmn > 100000) & (percentChange24h > 5):
            marketCap[coin.get('symbol')] = marketCapAmn
    sortedDict = {k: v for k, v in sorted(marketCap.items(), key=lambda item: item[1])}
    return sortedDict


def marketCapData():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '6000',
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
            if (quote == key) & (len(quotes) < 10) & (quote not in quotes):
                # diff = getDiff(marketCapValue, price)
                # if diff < 5:
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


def strategyFeed(smallCapCoins):
    client = getClient()
    for coin in smallCapCoins:
        pair = coin + "BTC"
        strategy = BotStrategy3(pair)
        nextCoin = False
        while nextCoin is False:
            currentPriceDict = client.get_symbol_ticker(symbol=pair)
            currentPrice = currentPriceDict.get('price')
            trade = strategy.tick(currentPrice, nextCoin, 0)
            print(pair + "\n" + currentPrice)
            if trade is not None:
                if trade.status == 'CLOSED':
                    nextCoin = True
            sleep(150)


def getHistoricalStart(days):
    historicalDate = date.today() - timedelta(days)
    dt = datetime.combine(historicalDate, datetime.min.time())
    ts = datetime.timestamp(dt)
    return ts.__int__()


def backTestFeed(smallCapCoins):
    client = getClient()
    nextCoin = False
    newCoinList = []
    backTestStartTS = getHistoricalStart(days=90)
    for coin in smallCapCoins:
        pair = coin + "BTC"
        output = BotLog()
        strategy = BotStrategy3(pair)
        historicalOutput = client.get_historical_klines(symbol=pair, interval="30m", start_str=1628942428000)
        for kline in historicalOutput:
            currentPrice = kline[4]
            timestamp = kline[0]
            trade = strategy.tick(currentPrice, nextCoin, timestamp)
            nextCoin = False
            print(pair + "\n" + currentPrice)
            if trade is not None:
                if trade.status == 'CLOSED':
                    if trade.getProfit() > 0:
                        newCoinList.append(coin)
                        break
        nextCoin = True


def Main():
    start = getHistoricalStart(90)
    print(start)
    # while True:
    #     baseBTC = binanceData()
    #     marketCapDict = marketCapData()
    #     smallCapCoins = compare(baseBTC, marketCapDict)
    #     print(smallCapCoins)
    #     if smallCapCoins is not "No Match":
    #         backTestFeed(smallCapCoins)
    #         #sleep(1800)
    #         break
    #     else:
    #         sleep(1800)


if __name__ == "__main__":
    Main()
