import sys
import time

from urllib.error import URLError
import os
from time import sleep
from pythonic_binance.client import Client

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

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
        if coin.get('quote').get('USD').get('market_cap') != 0:
            marketCap[coin.get('symbol')] = (coin.get('quote').get('USD').get('market_cap'))
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
    baseBTC = []
    client = getClient()
    info = client.get_all_tickers()
    for coin in info:
        if 'BTC' in coin.get('symbol')[3:]:
            market = coin.get('symbol')
            base = market[:-3]
            baseBTC.append("BTC" + base)
    return baseBTC


def compare(baseBTC, marketCapDict):
    quotes = []
    for key, value in marketCapDict.items():
        for quote in baseBTC:
            if (quote == key) & len(quotes) < 5:
                quotes.append(quote)
    return "No Match"


def strategyFeed(smallCapCoins):
    client = getClient()
    for coin in smallCapCoins:
        strategy = BotStrategy3(coin)
        nextCoin = False
        while nextCoin is False:
            currentPriceDict = client.get_symbol_ticker(symbol=coin)
            currentPrice = currentPriceDict.get('price')
            trade = strategy.tick(currentPrice, )
            if trade is not None:
                if trade.status == 'CLOSED':
                    nextCoin = True
            sleep(2)


def Main():
    while True:
        # bastBTC = binanceData()
        # marketCapDict = marketCapData()
        # result = compare(bastBTC, marketCapDict)
        result = ["LTCBTC"]
        if result is not "No Match":
            strategyFeed(result)
            print(result)
        sleep(1000)


if __name__ == "__main__":
    Main()
